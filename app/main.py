from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import (
    FEATURE_ORDER,
    INPUT_MAGNITUDES,
    METRICS,
    MODEL_VERSION,
    R_MAX,
    R_MIN,
    REDSHIFT_DOMAIN,
)
from app.model import is_loaded, load_model, predict
from app.schemas import (
    BatchInput,
    BatchOutput,
    PhotometryInput,
    PredictionOutput,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(
    title="Photo-z Serving API",
    description="Predicts photometric redshift for SDSS galaxies from u, g, r, i, z magnitudes.",
    version=MODEL_VERSION,
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "An unexpected error occurred."},
    )


def _to_output(item: PhotometryInput) -> PredictionOutput:
    redshift, magnitude_range = predict(item.u, item.g, item.r, item.i, item.z)
    return PredictionOutput(
        redshift=redshift,
        magnitude_range=magnitude_range,
        model_version=MODEL_VERSION,
    )


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": is_loaded()}


@app.get("/model/info")
def model_info():
    return {
        "model_version": MODEL_VERSION,
        "features": FEATURE_ORDER,
        "input_magnitudes": INPUT_MAGNITUDES,
        "metrics": METRICS,
        "valid_r_band_range": {"min": R_MIN, "max": R_MAX},
        "redshift_domain": REDSHIFT_DOMAIN,
    }


@app.post("/predict", response_model=PredictionOutput)
def predict_redshift(payload: PhotometryInput):
    return _to_output(payload)


@app.post("/predict/batch", response_model=BatchOutput)
def predict_batch(payload: BatchInput):
    return BatchOutput(predictions=[_to_output(item) for item in payload.items])