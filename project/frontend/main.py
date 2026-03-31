import streamlit as st

st.set_page_config(page_title="Network Threat Prediction", page_icon="🛡️", layout="wide")

def home():
    st.title("🛡️ Network Traffic Threat Prediction")
    st.write("원하는 입력 방식을 선택하세요.")

    col1, col2 = st.columns(2)

    with col1:
        st.page_link("log_search_frontend.py", label="CSV 입력", icon="📁")
        st.markdown(
            """
            <div style="
                padding:18px;
                border-radius:16px;
                background-color:#f8f9fa;
                border:1px solid #e6e6e6;
                margin-top:10px;
                min-height:220px;
            ">
                <h4 style="margin-top:0;">로그 일괄 분석 (CSV File Upload)</h4>
                <p style="font-size:15px; line-height:1.7;">
                    수집된 CSV 로그 파일을 업로드하여 대규모 트래픽 속에 숨겨진 위협을 일괄 탐색하세요.
                    전체적인 보안 현황 리포트와 함께 우선순위 대응 방안을 제시해 드립니다.
                </p>
                <p style="font-size:14px; color:#444;">
                    <b>사용법:</b> 규격에 맞춘 CSV 파일을 업로드하면 모델이 데이터를 조사합니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.page_link("app.py", label="직접 입력", icon="✍️")
        st.markdown(
            """
            <div style="
                padding:18px;
                border-radius:16px;
                background-color:#f8f9fa;
                border:1px solid #e6e6e6;
                margin-top:10px;
                min-height:220px;
            ">
                <h4 style="margin-top:0;">의심되는 특정 네트워크 흐름이 있나요?</h4>
                <p style="font-size:15px; line-height:1.7;">
                    10가지 핵심 지표를 직접 입력하여 해당 트래픽의 공격 여부와 유형을 진단받으세요.
                    즉각적인 위협 식별과 맞춤형 대응 가이드를 제공합니다.
                </p>
                <p style="font-size:14px; color:#444;">
                    <b>사용법:</b> 네트워크 장비에서 추출된 10개 피처 값을 입력창에 넣고
                    <b>'분석하기'</b>를 누르세요.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

pg = st.navigation([
    st.Page(home, title="메인", icon="🏠"),
    st.Page("log_search_frontend.py", title="CSV 입력", icon="📁"),
    st.Page("app.py", title="직접입력", icon="✍️"),
], position="sidebar")

import streamlit as st

st.set_page_config(page_title="Network Threat Prediction", page_icon="🛡️", layout="wide")

def home():
    st.title("🛡️ Network Traffic Threat Prediction")
    st.write("원하는 입력 방식을 선택하세요.")

    col1, col2 = st.columns(2)

    with col1:
        st.page_link("log_search_frontend.py", label="CSV 입력", icon="📁")
        st.markdown(
            """
            <div style="
                padding:18px;
                border-radius:16px;
                background-color:#f8f9fa;
                border:1px solid #e6e6e6;
                margin-top:10px;
                min-height:220px;
            ">
                <h4 style="margin-top:0;">로그 일괄 분석 (CSV File Upload)</h4>
                <p style="font-size:15px; line-height:1.7;">
                    수집된 CSV 로그 파일을 업로드하여 대규모 트래픽 속에 숨겨진 위협을 일괄 탐색하세요.
                    전체적인 보안 현황 리포트와 함께 우선순위 대응 방안을 제시해 드립니다.
                </p>
                <p style="font-size:14px; color:#444;">
                    <b>사용법:</b> 규격에 맞춘 CSV 파일을 업로드하면 모델이 데이터를 조사합니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.page_link("app.py", label="직접 입력", icon="✍️")
        st.markdown(
            """
            <div style="
                padding:18px;
                border-radius:16px;
                background-color:#f8f9fa;
                border:1px solid #e6e6e6;
                margin-top:10px;
                min-height:220px;
            ">
                <h4 style="margin-top:0;">의심되는 특정 네트워크 흐름이 있나요?</h4>
                <p style="font-size:15px; line-height:1.7;">
                    10가지 핵심 지표를 직접 입력하여 해당 트래픽의 공격 여부와 유형을 진단받으세요.
                    즉각적인 위협 식별과 맞춤형 대응 가이드를 제공합니다.
                </p>
                <p style="font-size:14px; color:#444;">
                    <b>사용법:</b> 네트워크 장비에서 추출된 10개 피처 값을 입력창에 넣고
                    <b>'분석하기'</b>를 누르세요.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

pg = st.navigation([
    st.Page(home, title="메인", icon="🏠"),
    st.Page("log_search_frontend.py", title="CSV 입력", icon="📁"),
    st.Page("app.py", title="직접입력", icon="✍️"),
], position="sidebar")

pg.run()