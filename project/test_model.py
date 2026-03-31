# 임시 파일. 삭제할 거임
from app.ml.model_loader import step1_model, step2_model

print("step1 classes:", step1_model.classes_)

if hasattr(step2_model, "classes_"):
    print("step2 classes:", step2_model.classes_)

    
