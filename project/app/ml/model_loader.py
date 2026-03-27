import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model_files")

STEP1_MODEL_PATH = os.path.join(MODEL_DIR, "hybrid_step1_binary.pkl")
STEP2_MODEL_PATH = os.path.join(MODEL_DIR, "hybrid_step2_multi.pkl")

step1_model = joblib.load(STEP1_MODEL_PATH)
step2_model = joblib.load(STEP2_MODEL_PATH)


# 로딩이 오래걸릴 때 확인했던 코드/ 최종코드엔 삭제하기
# import os
# import time
# import joblib

# start_all = time.time()
# print("모델 로딩 시작")

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# MODEL_DIR = os.path.join(BASE_DIR, "model_files")

# STEP1_MODEL_PATH = os.path.join(MODEL_DIR, "hybrid_step1_binary.pkl")
# STEP2_MODEL_PATH = os.path.join(MODEL_DIR, "hybrid_step2_multi.pkl")

# start = time.time()
# step1_model = joblib.load(STEP1_MODEL_PATH)
# print("step1 로딩 완료:", time.time() - start)

# start = time.time()
# step2_model = joblib.load(STEP2_MODEL_PATH)
# print("step2 로딩 완료:", time.time() - start)

# print("전체 모델 로딩 완료:", time.time() - start_all)