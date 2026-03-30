from typing import List

from openai import OpenAI

from app.prompts.mitre_prompt import MODEL
from app.schemas import ChatMessage


CHAT_DEVELOPER_PROMPT = """
너는 네트워크 보안 분석 보조 챗봇이다.

사용자는 이미 모델 예측 결과와 MITRE ATT&CK 기반 1차 분석 결과를 받은 상태다.
너의 역할은 그 분석 내용을 바탕으로 사용자의 추가 질문에 답하는 것이다.

규칙:
1. 반드시 제공된 analysis_context와 chat_history를 바탕으로 답하라.
2. 없는 사실은 지어내지 마라.
3. 분석 결과 범위를 넘는 내용은 "추가 확인 필요"라고 말하라.
4. 답변은 발표/데모에서 바로 읽을 수 있게 간결하고 명확하게 작성하라.
5. 보안 대응 방안, MITRE ATT&CK 후보, 공격 의미를 질문받으면 우선적으로 설명하라.
""".strip()


def build_chat_input(
    analysis_context: str,
    chat_history: List[ChatMessage],
    question: str,
):
    messages = [
        {
            "role": "developer",
            "content": CHAT_DEVELOPER_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"다음은 기존 1차 분석 결과이다.\n\n"
                f"{analysis_context}\n\n"
                f"이 분석 결과를 바탕으로 이후 질문에 답하라."
            ),
        },
    ]

    for msg in chat_history:
        messages.append(
            {
                "role": msg.role,
                "content": msg.content,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    return messages


def chat_with_analysis(
    analysis_context: str,
    chat_history: List[ChatMessage],
    question: str,
) -> str:
    client = OpenAI()

    input_messages = build_chat_input(
        analysis_context=analysis_context,
        chat_history=chat_history,
        question=question,
    )

    response = client.responses.create(
        model=MODEL,
        input=input_messages,
    )

    return response.output_text