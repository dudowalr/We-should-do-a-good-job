from app.ml.model_loader import step1_model, step2_model
from app.ml.preprocess import make_model_input

def run_prediction(input_features_json: dict):
    X = make_model_input(input_features_json)

    step1_pred = step1_model.predict(X)[0]

    if hasattr(step1_model, "predict_proba"):
        step1_proba = step1_model.predict_proba(X)[0]
        confidence_score = float(max(step1_proba))
    else:
        confidence_score = None

    if step1_pred == 0:
        predicted_label = "Benign"
    else:
        predicted_label = step2_model.predict(X)[0]

        if hasattr(step2_model, "predict_proba"):
            step2_proba = step2_model.predict_proba(X)[0]
            confidence_score = float(max(step2_proba))

    return {
        "predicted_label": str(predicted_label),
        "confidence_score": confidence_score
    }