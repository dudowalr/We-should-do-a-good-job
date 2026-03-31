import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model_files")

STEP1_MODEL_PATH = os.path.join(MODEL_DIR, "hybrid_step1_binary.pkl")
STEP2_MODEL_PATH = os.path.join(MODEL_DIR, "hybrid_step2_multi.pkl")

step1_model = joblib.load(STEP1_MODEL_PATH)
step2_model = joblib.load(STEP2_MODEL_PATH)