from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "photoz_xgb.json"

FEATURE_ORDER = ["u", "g", "r", "i", "z", "u_g", "g_r", "r_i", "i_z"]
INPUT_MAGNITUDES = ["u", "g", "r", "i", "z"]

MODEL_VERSION = "1.0.0"

R_MIN = 14.0
R_MAX = 22.0

METRICS = {"mae": 0.0168, "rmse": 0.0324, "r2": 0.5517}
REDSHIFT_DOMAIN = {"min": 0.0, "max": 1.0}