import pandas as pd
import streamlit as st

from log_search_service import LogSearchService

st.set_page_config(page_title="유사 로그 탐지 + AI 해석", page_icon="🔎", layout="wide")

service = LogSearchService()
all_df, loaded_files, load_warnings = service.load_all_logs()

if "search_bundle" not in st.session_state:
    st.session_state.search_bundle = None
if "last_keyword" not in st.session_state:
    st.session_state.last_keyword = ""
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

st.title("🔎 유사 로그 탐지 + AI 해석")
st.caption("메인 예측 화면과 분리된 협업용 보조 도구입니다. 비슷한 로그를 찾고, 반복 특징과 의미를 AI가 설명합니다.")

with st.sidebar:
    st.subheader("이 화면의 역할")
    st.write("- CSV 로그에서 유사 사례 찾기")
    st.write("- 빈도와 반복 패턴 요약")
    st.write("- function calling 기반 AI 해석")
    st.write("- 결과 CSV 저장 후 File Search로 유사 사례 설명")
    st.divider()
    st.write(f"로드된 파일 수: {len(loaded_files)}")
    st.write(f"전체 로그 수: {len(all_df)}")
    if st.button("새로고침"):
        st.cache_data.clear()
        st.rerun()

metric1, metric2, metric3 = st.columns(3)
metric1.metric("전체 로그 수", int(len(all_df)))
metric2.metric("CSV 파일 수", len(loaded_files))
metric3.metric("검색 핵심 컬럼 수", len(service.get_searchable_columns(all_df)) if not all_df.empty else 0)

for warning in load_warnings:
    st.warning(warning)

with st.expander("로드된 파일과 컬럼 보기"):
    st.write("파일 목록", loaded_files)
    st.write("컬럼 목록", list(all_df.columns) if not all_df.empty else [])

input_col, btn_col = st.columns([5, 1])
with input_col:
    keyword = st.text_input(
        "검색어 입력",
        value=st.session_state.last_keyword,
        placeholder="예: DDoS, Botnet, High, Suspicious, 특정 IP",
    )
with btn_col:
    search_clicked = st.button("검색", use_container_width=True)

quick_cols = st.columns(4)
for idx, quick_keyword in enumerate(["DDoS", "Botnet", "High", "Suspicious"]):
    if quick_cols[idx].button(quick_keyword, use_container_width=True):
        st.session_state.last_keyword = quick_keyword
        st.session_state.search_bundle = service.run_search_bundle(all_df, quick_keyword)
        st.session_state.ai_result = None
        st.rerun()

if search_clicked:
    if not keyword.strip():
        st.warning("검색어를 입력하세요.")
    elif all_df.empty:
        st.error("검색 가능한 로그가 없습니다.")
    else:
        st.session_state.last_keyword = keyword
        st.session_state.search_bundle = service.run_search_bundle(all_df, keyword)
        st.session_state.ai_result = None

bundle = st.session_state.search_bundle
if bundle is None:
    st.info("검색어를 입력하고 유사 로그를 찾아보세요.")
else:
    if bundle.result_df.empty:
        st.info("일치하는 유사 로그가 없습니다.")
    else:
        st.success(f"유사 로그 {len(bundle.result_df)}건을 찾았습니다.")

        top1, top2, top3 = st.columns(3)
        top1.metric("유사 로그 수", bundle.stats["row_count"])
        top2.metric("파일 수", len(bundle.stats.get("files", {})))
        top3.metric("공격 유형 수", len(bundle.stats.get("attack_type_counts", {})))

        summary_tab, result_tab, stats_tab, guide_tab, ai_tab = st.tabs(
            ["한눈에 보기", "원본 결과", "요약 통계", "점검 가이드", "AI 해석"]
        )

        with summary_tab:
            st.write(service.summarize_similar_logs(st.session_state.last_keyword, bundle.stats))
            st.write(service.describe_repeated_features(bundle.stats))
            st.write(service.extract_note_patterns(bundle.result_df))

        with result_tab:
            st.dataframe(bundle.result_df[bundle.ordered_columns], use_container_width=True)

        with stats_tab:
            if bundle.stats.get("files"):
                st.markdown("#### 파일별 건수")
                st.dataframe(
                    pd.DataFrame(list(bundle.stats["files"].items()), columns=["source_file", "count"]),
                    use_container_width=True,
                )
            if bundle.stats.get("attack_type_counts"):
                st.markdown("#### 공격 유형 분포")
                st.dataframe(
                    pd.DataFrame(list(bundle.stats["attack_type_counts"].items()), columns=["attack_type", "count"]),
                    use_container_width=True,
                )
            if bundle.stats.get("risk_level_counts"):
                st.markdown("#### 위험도 분포")
                st.dataframe(
                    pd.DataFrame(list(bundle.stats["risk_level_counts"].items()), columns=["risk_level", "count"]),
                    use_container_width=True,
                )
            if bundle.stats.get("protocol_counts"):
                st.markdown("#### 프로토콜 분포")
                st.dataframe(
                    pd.DataFrame(list(bundle.stats["protocol_counts"].items()), columns=["protocol", "count"]),
                    use_container_width=True,
                )
            if bundle.stats.get("time_range"):
                st.markdown("#### 발생 시각 범위")
                st.json(bundle.stats["time_range"])
            if bundle.stats.get("numeric_ranges"):
                st.markdown("#### 수치 범위")
                st.json(bundle.stats["numeric_ranges"])

        with guide_tab:
            st.write(bundle.response_guide)

        with ai_tab:
            st.write(
                "이 기능은 function calling으로 요약과 반복 특징을 먼저 만들고, 검색 결과를 CSV로 저장한 뒤 File Search로 유사 사례 의미를 해석합니다."
            )
            run_ai = st.button("유사 사례 AI 해석 실행", use_container_width=True)
            if run_ai:
                with st.spinner("AI가 유사 로그를 해석하는 중입니다..."):
                    try:
                        st.session_state.ai_result = service.run_ai_interpretation(
                            st.session_state.last_keyword,
                            bundle.result_df,
                            bundle.stats,
                        )
                    except Exception as exc:
                        st.session_state.ai_result = {"error": str(exc)}

            if st.session_state.ai_result:
                if "error" in st.session_state.ai_result:
                    st.error(f"AI 해석 실패: {st.session_state.ai_result['error']}")
                else:
                    st.markdown("#### 유사 사례 AI 해석 결과")
                    st.write(st.session_state.ai_result["analysis_text"])
                    st.caption(f"검색 결과 CSV: {st.session_state.ai_result['csv_path']}")
                    st.caption(f"분석 TXT: {st.session_state.ai_result['txt_path']}")
                    st.caption(f"업로드된 파일 ID: {st.session_state.ai_result['uploaded_file_id']}")
                    st.caption(f"Vector Store ID: {st.session_state.ai_result['vector_store_id']}")
