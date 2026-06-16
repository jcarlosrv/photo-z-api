import numpy as np
import xgboost as xgb

from app.config import FEATURE_ORDER, MODEL_PATH, R_MAX, R_MIN

_booster: xgb.Booster | None = None


def load_model() -> xgb.Booster:
    global _booster
    if _booster is None:
        b = xgb.Booster()
        b.load_model(str(MODEL_PATH))
        _booster = b
    return _booster


def is_loaded() -> bool:
    return _booster is not None


def classify_range(r: float) -> str:
    if r < R_MIN:
        return "below"
    if r > R_MAX:
        return "above"
    return "in"


def predict(u: float, g: float, r: float, i: float, z: float) -> tuple[float, str]:
    values = {
        "u": u, "g": g, "r": r, "i": i, "z": z,
        "u_g": u - g, "g_r": g - r, "r_i": r - i, "i_z": i - z,
    }
    row = np.array([[values[name] for name in FEATURE_ORDER]], dtype=float)
    dmatrix = xgb.DMatrix(row, feature_names=FEATURE_ORDER)
    redshift = float(load_model().predict(dmatrix)[0])
    return redshift, classify_range(r)