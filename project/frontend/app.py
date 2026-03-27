import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
import plotly.express as px
import pandas as pd

## 추가(db)
import requests
import uuid
##

## api 주소 추가(db)
FASTAPI_PREDICT_API_URL = os.getenv(
    "FASTAPI_PREDICT_API_URL",
    "http://127.0.0.1:8000/predict/"
)

FASTAPI_FEEDBACK_API_URL = os.getenv(
    "FASTAPI_FEEDBACK_API_URL",
    "http://127.0.0.1:8000/feedback/"
)
##

## 세션 상태 추가 (db)

if "incident_id" not in st.session_state:
    st.session_state.incident_id = None
##



load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="Network Traffic Threat Prediction", page_icon="🛡️", layout="wide")

st.title("🛡️ Network Traffic Threat Prediction App")
st.write("10개의 네트워크 입력값을 받아 결과를 보여줍니다.")

# 세션 상태 초기화
if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_features" not in st.session_state:
    st.session_state.last_features = None

if "is_helpful" not in st.session_state:
    st.session_state.is_helpful = None


def chatbot_response(user_message):
    messages = [
        {
            "role": "system",
            "content": "simply answer what kind of network threat it is."
        }
    ]

    for role, message in st.session_state.chat_history:
        messages.append({"role": role, "content": message})

    messages.append({"role": "user", "content": user_message})

    response = client.responses.create(
        model="gpt-5",
        input=messages
    )

    return response.output_text


# 예측 로직 함수 => 주석처리(db)
# def predict_result(features):
#     score = 0

#     if features["Flow Duration"] > 500000:
#         score += 1
#     if features["Flow Bytes/s"] > 100000:
#         score += 1
#     if features["Flow Packets/s"] > 1000:
#         score += 1
#     if features["Packet Length Mean"] > 800:
#         score += 1
#     if features["Init Fwd Win Bytes"] < 1000:
#         score += 1

#     if score >= 3:
#         return "⚠️ Suspicious Traffic Detected"
#     else:
#         return "✅ Normal Traffic"

## 실제 API 호출로 교체(db)
def predict_result(features):
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


## 피드백 전송 함수 추가(db)
def send_feedback(incident_log_id, is_helpful, rating=None, feedback_text=None):
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
##

# 입력 UI
st.subheader("1. Input Features")

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


# Submit 버튼 => 주섟처리(db)
# if st.button("Submit"):
#     features = {
#         "Flow Duration": flow_duration,
#         "Total Fwd Packets": total_fwd_packets,
#         "Total Backward Packets": total_backward_packets,
#         "Fwd Packet Length Mean": fwd_packet_length_mean,
#         "Bwd Packet Length Mean": bwd_packet_length_mean,
#         "Flow Bytes/s": flow_bytes_s,
#         "Flow Packets/s": flow_packets_s,
#         "Flow IAT Mean": flow_iat_mean,
#         "Packet Length Mean": packet_length_mean,
#         "Init Fwd Win Bytes": init_fwd_win_bytes
#     }

#     result = predict_result(features)
#     st.session_state.prediction_result = result
#     st.session_state.last_features = features
#     st.session_state.is_helpful = None

## Submit 버튼 수정(db)
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
        except requests.exceptions.RequestException as e:
            st.error(f"예측 API 호출 실패: {e}")
            st.session_state.prediction_result = None
            st.session_state.incident_id = None
##

# 결과 표시 영역 => 주석(db)
# st.subheader("2. Prediction Result")

# if st.session_state.prediction_result is not None:
#     if "Suspicious" in st.session_state.prediction_result:
#         st.error(st.session_state.prediction_result)
#     else:
#         st.success(st.session_state.prediction_result)

#     st.markdown("### 도움이 돼셨나요?")

#     col_help1, col_help2 = st.columns(2)

#     with col_help1:
#         if st.button("👍 예"):
#             st.session_state.is_helpful = True

#     with col_help2:
#         if st.button("👎 아니요"):
#             st.session_state.is_helpful = False

#     if st.session_state.is_helpful is True:
#         st.success("도움을 드려서 기쁩니다.")
#     elif st.session_state.is_helpful is False:
#         st.warning("도움을 드리지 못하여 죄송 합니다.")
# else:
#     st.info("아직 결과가 없습니다. 입력값을 넣고 Submit 버튼을 눌러주세요.")


# 결과 표시 영역 수정
st.subheader("2. Prediction Result")

if st.session_state.prediction_result is not None:
    result = st.session_state.prediction_result

    predicted_label = result.get("predicted_label")
    confidence_score = result.get("confidence_score")
    risk_level = result.get("risk_level")
    anomaly_summary = result.get("anomaly_summary")
    kill_chain_stage = result.get("kill_chain_stage")
    defense_mechanism = result.get("defense_mechanism")
    llm_recommendation = result.get("llm_recommendation")

    if risk_level == "High":
        st.error(f"탐지 결과: {predicted_label}")
    else:
        st.success(f"탐지 결과: {predicted_label}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(
            "Confidence Score",
            f"{confidence_score:.4f}" if confidence_score is not None else "-"
        )
    with col_b:
        st.metric("Risk Level", risk_level if risk_level else "-")

    if anomaly_summary:
        st.markdown("### Anomaly Summary")
        st.write(anomaly_summary)

    if kill_chain_stage:
        st.markdown("### Kill Chain Stage")
        st.write(kill_chain_stage)

    if defense_mechanism:
        st.markdown("### Defense Mechanism")
        st.write(defense_mechanism)

    if llm_recommendation:
        st.markdown("### Recommendation")
        st.write(llm_recommendation)

    st.markdown("### 도움이 돼셨나요?")

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




# Plotly 차트 영역
st.subheader("3. Input Feature Visualization")

if st.session_state.last_features is not None:
    feature_df = pd.DataFrame({
        "Feature": list(st.session_state.last_features.keys()),
        "Value": list(st.session_state.last_features.values())
    })

    fig = px.bar(
        feature_df,
        x="Feature",
        y="Value",
        title="Input Feature Values",
        text="Value"
    )

    fig.update_layout(
        xaxis_title="Features",
        yaxis_title="Values",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("아직 시각화할 입력값이 없습니다.")

# 챗봇 영역
st.subheader("4. Chatbot")

for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)

user_chat = st.chat_input("챗봇에게 질문해보세요!")

if user_chat:
    st.session_state.chat_history.append(("user", user_chat))

    bot_reply = chatbot_response(user_chat)
    st.session_state.chat_history.append(("assistant", bot_reply))

    st.rerun()