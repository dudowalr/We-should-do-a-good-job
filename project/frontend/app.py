import os
import uuid

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from streamlit_float import float_init, float_css_helper
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# API URLs
# ----------------------------
FASTAPI_PREDICT_API_URL = os.getenv(
    "FASTAPI_PREDICT_API_URL",
    "http://127.0.0.1:8000/predict/"
)

FASTAPI_FEEDBACK_API_URL = os.getenv(
    "FASTAPI_FEEDBACK_API_URL",
    "http://127.0.0.1:8000/feedback/"
)

FASTAPI_CHAT_API_URL = os.getenv(
    "FASTAPI_CHAT_API_URL",
    "http://127.0.0.1:8000/chat/"
)



# ----------------------------
# Streamlit page config
# ----------------------------
st.set_page_config(
    page_title="Network Traffic Threat Prediction",
    page_icon="🛡️",
    layout="wide"
)

float_init()

st.title("🛡️ Network Traffic Threat Prediction App")
st.write("10개의 네트워크 입력값을 받아 예측 결과와 보안 분석 결과를 보여줍니다.")



# ----------------------------
# Session state init
# ----------------------------
if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

if "last_features" not in st.session_state:
    st.session_state.last_features = None

if "incident_id" not in st.session_state:
    st.session_state.incident_id = None

if "is_helpful" not in st.session_state:
    st.session_state.is_helpful = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "analysis_context" not in st.session_state:
    st.session_state.analysis_context = None

if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

if "chat_input_text" not in st.session_state:
    st.session_state.chat_input_text = ""

# ----------------------------
# API helper functions
# ----------------------------
def predict_result(features: dict) -> dict:
    payload = {
        "session_id": str(uuid.uuid4()),
        "input_features_json": features
    }

    response = requests.post(
        FASTAPI_PREDICT_API_URL,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    return response.json()


def send_feedback(incident_log_id, is_helpful, rating=None, feedback_text=None) -> dict:
    payload = {
        "incident_log_id": incident_log_id,
        "rating": rating,
        "feedback_text": feedback_text,
        "is_helpful": is_helpful
    }

    response = requests.post(
        FASTAPI_FEEDBACK_API_URL,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def ask_chatbot(question: str) -> str:
    payload = {
        "analysis_context": st.session_state.analysis_context or "",
        "chat_history": st.session_state.chat_history,
        "question": question
    }

    response = requests.post(
        FASTAPI_CHAT_API_URL,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    return response.json()["answer"]


# ----------------------------
# Input UI
# ----------------------------
st.subheader("Input Features")

col1, col2 = st.columns(2)

with col1:
    flow_duration = st.number_input("Flow Duration", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")
    total_fwd_packets = st.number_input("Total Fwd Packets", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")
    total_backward_packets = st.number_input("Total Backward Packets", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")
    fwd_packet_length_mean = st.number_input("Fwd Packet Length Mean", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")
    bwd_packet_length_mean = st.number_input("Bwd Packet Length Mean", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")

with col2:
    flow_bytes_s = st.number_input("Flow Bytes/s", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")
    flow_packets_s = st.number_input("Flow Packets/s", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")
    flow_iat_mean = st.number_input("Flow IAT Mean", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")
    packet_length_mean = st.number_input("Packet Length Mean", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")
    init_fwd_win_bytes = st.number_input("Init Fwd Win Bytes", min_value=0, value=None, step=1, placeholder="값을 입력 하세요")

if st.button("Submit"):
    if None in [
        flow_duration,
        total_fwd_packets,
        total_backward_packets,
        fwd_packet_length_mean,
        bwd_packet_length_mean,
        flow_bytes_s,
        flow_packets_s,
        flow_iat_mean,
        packet_length_mean,
        init_fwd_win_bytes
    ]:
        st.error("모든 값을 입력해주세요.")
    else:
        features = {
            "Flow Duration": flow_duration,
            "Total Fwd Packets": total_fwd_packets,
            "Total Backward Packets": total_backward_packets,
            "Fwd Packet Length Mean": fwd_packet_length_mean,
            "Bwd Packet Length Mean": bwd_packet_length_mean,
            "Flow Bytes/s": flow_bytes_s,
            "Flow Packets/s": flow_packets_s,
            "Flow IAT Mean": flow_iat_mean,
            "Packet Length Mean": packet_length_mean,
            "Init Fwd Win Bytes": init_fwd_win_bytes
        }

        try:
            result = predict_result(features)

            st.session_state.prediction_result = result
            st.session_state.last_features = features
            st.session_state.is_helpful = None
            st.session_state.incident_id = result.get("id")

            # 챗봇 초기화 및 첫 분석 결과를 assistant 메시지로 저장
            st.session_state.chat_history = []
            st.session_state.analysis_context = result.get("llm_recommendation")

            if result.get("llm_recommendation"):
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": result["llm_recommendation"]
                    }
                )

        except requests.exceptions.RequestException as e:
            st.error(f"예측 API 호출 실패: {e}")
            st.session_state.prediction_result = None
            st.session_state.last_features = None
            st.session_state.incident_id = None
            st.session_state.chat_history = []
            st.session_state.analysis_context = None


# ----------------------------
# Chatbot
# ----------------------------
fab_container = st.container()
st.markdown(
    """
    <style>
    .st-key-chat_fab_button button {
        background-color: black !important;
        color: white !important;
        border: 2px solid black !important;
        border-radius: 50% !important;
        width: 64px !important;
        height: 64px !important;
        font-size: 28px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with fab_container:
    col_a, col_b, col_c = st.columns([8, 1, 1])
    with col_c:
        if st.button("🗨️", key="chat_fab_button"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()


fab_container.float(
    float_css_helper(
        width="70px",
        bottom="20px",
        right="20px",
        transition=0
    )
)


if st.session_state.chat_open:
    chat_box = st.container(border=True)

    with chat_box:
        top_left, top_right = st.columns([6, 1])

        with top_left:
            st.markdown(
                '<h3 style="margin:0; color:#111111;">Chatbot</h3>',
                unsafe_allow_html=True
            )

        with top_right:
            if st.button("✖", key="close_chat_popup"):
                st.session_state.chat_open = False
                st.rerun()

        if not st.session_state.analysis_context:
            st.markdown(
                """
                <div style="
                    background-color: #f3f4f6;
                    color: #111111;
                    padding: 14px 16px;
                    border-radius: 12px;
                    border: 1px solid #d1d5db;
                    line-height: 1.6;
                    font-size: 14px;
                    white-space: normal;
                    word-break: keep-all;
                ">
                    먼저 예측을 실행하면 분석 결과를 바탕으로 챗봇과 대화할 수 있습니다.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            history_area = st.container(height=280)

            with history_area:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            with st.form("floating_chat_form", clear_on_submit=True, enter_to_submit=True):
                user_chat = st.text_input(
                    "질문 입력",
                    placeholder="질문을 입력하세요"
                )

                submitted = st.form_submit_button("전송", use_container_width=True)

                if submitted:
                    user_chat = user_chat.strip()

                    if user_chat:
                        st.session_state.chat_history.append(
                            {
                                "role": "user",
                                "content": user_chat
                            }
                        )

                        try:
                            bot_reply = ask_chatbot(user_chat)

                            st.session_state.chat_history.append(
                                {
                                    "role": "assistant",
                                    "content": bot_reply
                                }
                            )

                            st.rerun()

                        except requests.exceptions.RequestException as e:
                            st.error(f"챗봇 API 호출 실패: {e}")

    chat_box.float(
        float_css_helper(
            width="380px",
            bottom="95px",
            right="20px",
            transition=0
        )
        + """
        background-color: white;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        padding: 10px;
        z-index: 999990;
        """
    chat_box.float(
        float_css_helper(
            width="420px",
            bottom="95px",
            right="20px",
            transition=0
        )
        + """
        background-color: white;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        padding: 14px;
        z-index: 999990;
        max-height: 600px;
        overflow-y: auto;
        """
    )
    
# ----------------------------
# Prediction Result
# ----------------------------
st.subheader("Prediction Result")

if st.session_state.prediction_result is not None:
    result = st.session_state.prediction_result

    predicted_label = result.get("predicted_label")
    confidence_score = result.get("confidence_score")
    risk_level = result.get("risk_level")
    anomaly_summary = result.get("anomaly_summary")
    defense_mechanism = result.get("defense_mechanism")

    if risk_level == "High":
        st.error(f"탐지 결과: {predicted_label}")
    else:
        st.success(f"탐지 결과: {predicted_label}")

    col_a, col_b = st.columns(2)

    with col_a:
        if confidence_score is not None:
            st.metric("Confidence Score", f"{confidence_score * 100:.2f}%")
        else:
            st.metric("Confidence Score", "-")

    with col_b:
        st.metric("Risk Level", risk_level if risk_level else "-")

    if anomaly_summary:
        st.markdown("### Anomaly Summary")
        st.write(anomaly_summary)

    if defense_mechanism:
        st.markdown("### Defense Mechanism")
        st.write(defense_mechanism)

    st.markdown("### 도움이 되셨나요?")

    col_help1, col_help2 = st.columns(2)

    with col_help1:
        if st.button("👍 예"):
            st.session_state.is_helpful = True
            if st.session_state.incident_id is not None:
                try:
                    send_feedback(
                        incident_log_id=st.session_state.incident_id,
                        is_helpful=True,
                        rating=5,
                        feedback_text="도움이 되었습니다."
                    )
                    st.success("피드백이 저장되었습니다.")
                except requests.exceptions.RequestException as e:
                    st.error(f"피드백 저장 실패: {e}")

    with col_help2:
        if st.button("👎 아니요"):
            st.session_state.is_helpful = False
            if st.session_state.incident_id is not None:
                try:
                    send_feedback(
                        incident_log_id=st.session_state.incident_id,
                        is_helpful=False,
                        rating=1,
                        feedback_text="도움이 되지 않았습니다."
                    )
                    st.warning("피드백이 저장되었습니다.")
                except requests.exceptions.RequestException as e:
                    st.error(f"피드백 저장 실패: {e}")

    if st.session_state.is_helpful is True:
        st.success("도움을 드려서 기쁩니다.")
    elif st.session_state.is_helpful is False:
        st.warning("도움을 드리지 못하여 죄송합니다.")

else:
    st.info("아직 결과가 없습니다. 입력값을 넣고 Submit 버튼을 눌러주세요.")

# ----------------------------
# Visualization
# ----------------------------
# st.subheader("4. Input Feature Visualization")

# if st.session_state.last_features is not None:
#     feature_df = pd.DataFrame({
#         "Feature": list(st.session_state.last_features.keys()),
#         "Value": list(st.session_state.last_features.values())
#     })

#     fig = px.bar(
#         feature_df,
#         x="Feature",
#         y="Value",
#         title="Input Feature Values",
#         text="Value"
#     )

#     fig.update_layout(
#         xaxis_title="Features",
#         yaxis_title="Values",
#         xaxis_tickangle=-45
#     )

#     st.plotly_chart(fig, use_container_width=True)
# else:
#     st.info("아직 시각화할 입력값이 없습니다.")
