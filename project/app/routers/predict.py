from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PredictRequest, PredictResponse
from app.crud import create_incident_log
from app.ml.predictor import run_prediction
from app.services.mitre_analysis_service import analyze_mitre_with_openai

router = APIRouter()


@router.post("/", response_model=PredictResponse)
def predict(request: PredictRequest, db: Session = Depends(get_db)):
    try:
        result = run_prediction(request.input_features_json)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 중 오류 발생: {str(e)}")

    predicted_label = result["predicted_label"]
    confidence_score = result["confidence_score"]

    risk_level = "Low"
    anomaly_summary = None
    # kill_chain_stage = None  #안쓰는 col
    defense_mechanism = None
    llm_recommendation = None

    if predicted_label != "Benign":
        risk_level = "High"
        anomaly_summary = f"{predicted_label} 유형의 이상 트래픽이 탐지되었습니다."
        # kill_chain_stage = "추후 확정 필요"

        try:
            mitre_result_text = analyze_mitre_with_openai(
                predicted_label=predicted_label,
                confidence_score=confidence_score,
                input_features=request.input_features_json,
            )
            defense_mechanism = "OpenAI 분석 결과 참고"
            llm_recommendation = mitre_result_text
        except Exception as e:
            defense_mechanism = "OpenAI 분석 결과 참고"
            llm_recommendation = f"MITRE/OpenAI 분석 중 오류 발생: {str(e)}"

    else:
        anomaly_summary = "이상 징후가 발견되지 않았습니다."

    incident = create_incident_log(
        db=db,
        session_id=request.session_id,
        input_features_json=request.input_features_json,
        predicted_label=predicted_label,
        confidence_score=confidence_score,
        # kill_chain_stage=kill_chain_stage,
        defense_mechanism=defense_mechanism,
        llm_recommendation=llm_recommendation
    )

    return PredictResponse(
        id=incident.id,
        predicted_label=predicted_label,
        confidence_score=confidence_score,
        risk_level=risk_level,
        anomaly_summary=anomaly_summary,
        # kill_chain_stage=kill_chain_stage,
        defense_mechanism=defense_mechanism,
        llm_recommendation=llm_recommendation
    )