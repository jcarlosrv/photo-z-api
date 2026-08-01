# Infrastructure

AWS resource definitions, applied with the AWS CLI.

| File | Service | Purpose |
|---|---|---|
| `lambda-trust-policy.json` | IAM | Lets Lambda assume the function's execution role |
| `ecr-lifecycle.json` | ECR | Bounds image storage cost |
| `warmer-target.json` | EventBridge | Payload the scheduled warmer sends to the function |

`warmer-target.json` contains `<ACCOUNT_ID>` -- substitute a real account ID before applying.

## Execution role

Trust policy only; permissions come from the managed `AWSLambdaBasicExecutionRole`
(CloudWatch Logs, nothing else). The model ships inside the image and the function runs
outside a VPC, so there is nothing further to grant.

## Image retention

Untagged images expire after 1 day; only the 2 most recent `v*` images are kept.

Images are tagged `v1`, `v2`, ... not `latest`:

- An `imageCountMoreThan` rule selects on `tagPrefixList`, so a reused tag gives it
  nothing to count.
- Lambda pins an image tag to a digest at deploy time. Re-pushing the same tag does
  **not** update a running function -- that needs
  `aws lambda update-function-code --image-uri ...`. Nothing errors; the deploy silently
  doesn't take.

## Function URL access policy

Not a file here -- the CLI cannot fully express it.

A public Function URL needs **two** statements:

| Sid | Action | Condition |
|---|---|---|
| `FunctionURLAllowPublicAccess` | `lambda:InvokeFunctionUrl` | `StringEquals lambda:FunctionUrlAuthType = NONE` |
| `FunctionURLAllowInvokeAction` | `lambda:InvokeFunction` | `Bool lambda:InvokedViaFunctionUrl = true` |

Permission to *use the URL* and permission to *invoke the function* are separate. With
only the first, requests return `403 AccessDeniedException` at the authorization layer --
before the function runs, so nothing reaches CloudWatch Logs.

`add-permission` rejects the second statement:

```
--action lambda:InvokeFunction --principal "*" --function-url-auth-type NONE
-> InvalidParameterValueException: FunctionUrlAuthType is only supported for
   lambda:InvokeFunctionUrl action
```

Dropping the flag succeeds but grants *unconditional* public invoke, bypassing the URL
entirely. The condition is the point of the statement.

Create the Function URL in the console -- it writes both statements atomically. Confirm
with `aws lambda get-policy`.

## Warmer

EventBridge rule on `rate(5 minutes)`, invoking the function directly.

Because it bypasses the Function URL, the function receives an EventBridge event, and
Mangum raises `KeyError: 'sourceIp'` on anything that isn't an API Gateway event.
`warmer-target.json` supplies a constant synthetic API Gateway v2 event for `GET /health`
in the target's `Input` field -- no application code change.

Order: `put-rule` -> `add-permission` (principal `events.amazonaws.com`, `--source-arn`
set to the rule ARN) -> `put-targets` (expect `FailedEntryCount: 0`).

Without `--source-arn`, any EventBridge rule in any account could invoke this function.

A classic scheduled rule is used rather than EventBridge Scheduler: rules targeting AWS
services are free and need no IAM role.

## Log group

`/aws/lambda/photo-z-api` is created explicitly with 7-day retention. Letting Lambda
create it on first invocation leaves it on never-expire.
