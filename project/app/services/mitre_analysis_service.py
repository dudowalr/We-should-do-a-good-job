import json
from typing import Any, Dict

from openai import OpenAI

from app.prompts.mitre_prompt import MODEL, DEVELOPER_PROMPT


def build_mitre_input_payload(
    predicted_label: str,
    confidence_score: float,
    input_features: Dict[str, Any],
) -> Dict[str, Any]:
    predicted_class_label = predicted_label.split("-")[0] if predicted_label and "-" in predicted_label else predicted_label

    return {
        "analysis_result": {
            "predicted_label": predicted_label,
            "predicted_class_label": predicted_class_label,
            "confidence_score": confidence_score,
            "is_attack": predicted_label != "Benign",
            "input_features": input_features,
        }
    }


def build_user_prompt(data: Dict[str, Any], question: str) -> str:
    return f"""
다음은 네트워크 공격 분류 모델이 생성한 결과 JSON이다.
이 JSON만을 바탕으로 분석해라.

JSON:
{json.dumps(data, ensure_ascii=False, indent=2)}

질문:
{question}
""".strip()


def analyze_mitre_with_openai(
    predicted_label: str,
    confidence_score: float,
    input_features: Dict[str, Any],
    question: str = "지금 공격이 뭐고 대응방안 알려줘",
) -> str:
    client = OpenAI()

    payload = build_mitre_input_payload(
        predicted_label=predicted_label,
        confidence_score=confidence_score,
        input_features=input_features,
    )

    user_prompt = build_user_prompt(payload, question)

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "developer",
                "content": DEVELOPER_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.output_text