from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MAG_MIN = 0.0
MAG_MAX = 40.0
MAX_BATCH = 1000


class PhotometryInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {"u": 19.5, "g": 18.2, "r": 17.5, "i": 17.1, "z": 16.9}
        }
    )
    u: float = Field(ge=MAG_MIN, le=MAG_MAX)
    g: float = Field(ge=MAG_MIN, le=MAG_MAX)
    r: float = Field(ge=MAG_MIN, le=MAG_MAX)
    i: float = Field(ge=MAG_MIN, le=MAG_MAX)
    z: float = Field(ge=MAG_MIN, le=MAG_MAX)


class PredictionOutput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    redshift: float
    magnitude_range: Literal["in", "below", "above"]
    model_version: str


class BatchInput(BaseModel):
    items: list[PhotometryInput] = Field(min_length=1, max_length=MAX_BATCH)


class BatchOutput(BaseModel):
    predictions: list[PredictionOutput]