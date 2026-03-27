import glob
import json
import os
import time
import requests
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LOG_DIR = "logs"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLUMN_ALIASES = {
    "timestamp": ["timestamp", "time", "datetime", "date", "event_time"],
    "attack_type": ["attack_type", "Attack Type", "Label", "label", "type"],
    "risk_level": ["risk_level", "risk", "severity", "level"],
    "src_ip": ["src_ip", "source_ip", "Source IP", "src", "source"],
    "dst_ip": ["dst_ip", "destination_ip", "Destination IP", "dst", "destination"],
    "protocol": ["protocol", "Protocol", "proto"],
    "flow_packets_s": ["flow_packets_s", "Flow Packets/s", "packets_per_sec"],
    "flow_bytes_s": ["flow_bytes_s", "Flow Bytes/s", "bytes_per_sec"],
    "init_fwd_win_bytes": ["init_fwd_win_bytes", "Init Fwd Win Bytes", "fwd_win_bytes"],
    "note": ["note", "description", "memo", "comment"],
}

DISPLAY_PRIORITY = [
    "timestamp",
    "attack_type",
    "risk_level",
    "src_ip",
    "dst_ip",
    "protocol",
    "flow_packets_s",
    "flow_bytes_s",
    "init_fwd_win_bytes",
    "note",
    "source_file",
]


@dataclass
class SearchBundle:
    result_df: pd.DataFrame
    stats: Dict[str, Any]
    response_guide: str
    ordered_columns: List[str]


class LogSearchService:
    """Collaboration-friendly service layer for similar-log detection + AI interpretation."""

    def __init__(self, log_dir: str = LOG_DIR, output_dir: str = OUTPUT_DIR, api_key: Optional[str] = None):
        self.log_dir = log_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        key = (api_key or os.getenv("OPENAI_API_KEY") or "").strip()
        self.client = OpenAI(api_key=key) if key else None

        self.fastapi_csv_api_url = os.getenv(
            "FASTAPI_CSV_API_URL",
            "http://127.0.0.1:8000/csv-analysis/"
        )

    # ---------- data loading ----------
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        rename_map: Dict[str, str] = {}
        lower_to_original = {str(col).strip().lower(): col for col in df.columns}

        for standard_name, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                key = str(alias).strip().lower()
                if key in lower_to_original:
                    original = lower_to_original[key]
                    if original != standard_name:
                        rename_map[original] = standard_name
                    break

        return df.rename(columns=rename_map) if rename_map else df

    def load_all_logs(self) -> Tuple[pd.DataFrame, List[str], List[str]]:
        csv_files = sorted(glob.glob(os.path.join(self.log_dir, "*.csv")))
        if not csv_files:
            return pd.DataFrame(), [], [f"'{self.log_dir}' 폴더 안에 CSV 파일이 없습니다."]

        frames: List[pd.DataFrame] = []
        loaded_files: List[str] = []
        warnings: List[str] = []

        for file_path in csv_files:
            filename = os.path.basename(file_path)
            try:
                df = pd.read_csv(file_path)
                if df.empty:
                    warnings.append(f"{filename}: 비어 있는 파일입니다.")
                    continue
                df = self.normalize_columns(df)
                df["source_file"] = filename
                frames.append(df)
                loaded_files.append(filename)
            except Exception as exc:
                warnings.append(f"{filename} 읽기 실패: {exc}")

        if not frames:
            return pd.DataFrame(), loaded_files, warnings or ["유효한 로그 데이터를 읽지 못했습니다."]

        all_df = pd.concat(frames, ignore_index=True, sort=False)
        return all_df, loaded_files, warnings

    # ---------- base search / summary ----------
    def get_searchable_columns(self, df: pd.DataFrame) -> List[str]:
        preferred = [
            "attack_type",
            "risk_level",
            "src_ip",
            "dst_ip",
            "protocol",
            "timestamp",
            "note",
            "source_file",
        ]
        return [col for col in preferred if col in df.columns] or list(df.columns)

    def search_logs(self, df: pd.DataFrame, keyword: str) -> pd.DataFrame:
        keyword = str(keyword).strip()
        if not keyword or df.empty:
            return pd.DataFrame()

        keyword_lower = keyword.lower()
        condition = pd.Series(False, index=df.index)

        for col in self.get_searchable_columns(df):
            try:
                values = df[col].astype(str).str.lower()
                condition = condition | values.str.contains(keyword_lower, na=False, regex=False)
            except Exception:
                continue

        return df[condition].copy().drop_duplicates()

    def build_summary_stats(self, result_df: pd.DataFrame) -> Dict[str, Any]:
        stats: Dict[str, Any] = {
            "row_count": int(len(result_df)),
            "files": {},
            "attack_type_counts": {},
            "risk_level_counts": {},
            "protocol_counts": {},
            "time_range": {},
            "numeric_ranges": {},
        }

        if result_df.empty:
            return stats

        for key in ["source_file", "attack_type", "risk_level", "protocol"]:
            if key in result_df.columns:
                counts = result_df[key].astype(str).value_counts().head(10).to_dict()
                if key == "source_file":
                    stats["files"] = counts
                elif key == "attack_type":
                    stats["attack_type_counts"] = counts
                elif key == "risk_level":
                    stats["risk_level_counts"] = counts
                elif key == "protocol":
                    stats["protocol_counts"] = counts

        if "timestamp" in result_df.columns:
            parsed = pd.to_datetime(result_df["timestamp"], errors="coerce")
            valid = parsed.dropna()
            if not valid.empty:
                stats["time_range"] = {
                    "start": str(valid.min()),
                    "end": str(valid.max()),
                }

        for col in ["flow_packets_s", "flow_bytes_s", "init_fwd_win_bytes"]:
            if col in result_df.columns:
                numeric = pd.to_numeric(result_df[col], errors="coerce").dropna()
                if not numeric.empty:
                    stats["numeric_ranges"][col] = {
                        "min": float(numeric.min()),
                        "max": float(numeric.max()),
                        "mean": float(numeric.mean()),
                    }

        return stats

    def build_response_guide(self, stats: Dict[str, Any]) -> str:
        attack_counts = stats.get("attack_type_counts", {})
        risk_counts = stats.get("risk_level_counts", {})
        if not attack_counts:
            return "검색 결과가 적거나 attack_type 컬럼이 없어 대응가이드를 만들기 어렵습니다. 우선 원본 로그, 시간대 분포, source/destination 정보를 추가 확인하세요."

        top_attack = next(iter(attack_counts.keys()))
        top_risk = next(iter(risk_counts.keys()), "Unknown")
        guides = {
            "DDoS": [
                "짧은 시간에 packets/s, bytes/s가 급증했는지 먼저 확인합니다.",
                "동일 시간대 Source IP 분포와 반복 요청 패턴을 점검합니다.",
                "WAF, Rate Limit, 방화벽 차단 정책 적용 여부를 확인합니다.",
            ],
            "Botnet": [
                "외부 통신 대상과 주기적인 연결 패턴을 확인합니다.",
                "의심 호스트를 분리하고 IOC를 추가 수집합니다.",
                "DNS 조회 이력과 프로세스 행위를 함께 점검합니다.",
            ],
            "Suspicious": [
                "정상 기준선 대비 급변한 컬럼이 무엇인지 먼저 확인합니다.",
                "반복 발생 시간대와 특정 IP 집중 여부를 봅니다.",
                "같은 시점의 다른 로그와 함께 상관분석합니다.",
            ],
            "Normal": [
                "즉시 차단보다 기준선 데이터로 보관하는 편이 좋습니다.",
                "같은 형식으로 로그를 계속 축적해 향후 비교 기준을 만듭니다.",
            ],
        }
        action_lines = guides.get(
            top_attack,
            [
                "원본 로그와 반복 패턴을 먼저 확인합니다.",
                "의심 IP, 시간대, 프로토콜 분포를 추가 점검합니다.",
            ],
        )
        return (
            f"주요 탐지 유형은 '{top_attack}'이며 현재 위험도 분포상 '{top_risk}'가 가장 많이 보입니다.\n"
            + "\n".join([f"- {line}" for line in action_lines])
        )

    def ordered_columns(self, result_df: pd.DataFrame) -> List[str]:
        return [c for c in DISPLAY_PRIORITY if c in result_df.columns] + [
            c for c in result_df.columns if c not in DISPLAY_PRIORITY
        ]

    def run_search_bundle(self, df: pd.DataFrame, keyword: str) -> SearchBundle:
        result_df = self.search_logs(df, keyword)
        stats = self.build_summary_stats(result_df)
        response_guide = self.build_response_guide(stats)
        ordered_cols = self.ordered_columns(result_df)
        return SearchBundle(
            result_df=result_df,
            stats=stats,
            response_guide=response_guide,
            ordered_columns=ordered_cols,
        )

    # ---------- function-calling helpers ----------
    def _serialize_stats(self, stats: Dict[str, Any]) -> str:
        return json.dumps(stats, ensure_ascii=False, indent=2)

    def summarize_similar_logs(self, keyword: str, stats: Dict[str, Any]) -> str:
        row_count = stats.get("row_count", 0)
        attack_counts = stats.get("attack_type_counts", {})
        risk_counts = stats.get("risk_level_counts", {})
        file_counts = stats.get("files", {})

        lines = [f"키워드 '{keyword}'와 일치하는 로그 {row_count}건이 검색되었습니다."]

        if attack_counts:
            top_attack, top_count = next(iter(attack_counts.items()))
            lines.append(f"가장 많이 보이는 유형은 {top_attack}이며 {top_count}건입니다.")

        if risk_counts:
            top_risk, top_risk_count = next(iter(risk_counts.items()))
            lines.append(f"가장 많이 보이는 위험도는 {top_risk}이며 {top_risk_count}건입니다.")

        if file_counts:
            top_file, top_file_count = next(iter(file_counts.items()))
            lines.append(f"가장 많이 발견된 파일은 {top_file}이며 {top_file_count}건이 포함됩니다.")

        if stats.get("time_range"):
            lines.append(
                f"발생 시각 범위는 {stats['time_range'].get('start')} ~ {stats['time_range'].get('end')} 입니다."
            )

        return " ".join(lines)

    def describe_repeated_features(self, stats: Dict[str, Any]) -> str:
        ranges = stats.get("numeric_ranges", {})
        parts: List[str] = []

        for col, payload in ranges.items():
            parts.append(
                f"{col}는 대략 {payload['min']:.0f} ~ {payload['max']:.0f} 범위이며 평균은 {payload['mean']:.1f}입니다."
            )

        if not parts:
            return "수치형 반복 특징은 제한적으로 보입니다. attack_type, risk_level, note 같은 범주형/텍스트 패턴 위주로 확인이 필요합니다."

        return " ".join(parts)

    def extract_note_patterns(self, result_df: pd.DataFrame) -> str:
        if result_df.empty or "note" not in result_df.columns:
            return "note 컬럼이 없어 반복 설명 문구를 따로 추출하지 못했습니다."

        notes = result_df["note"].dropna().astype(str)
        if notes.empty:
            return "note 컬럼 값이 비어 있어 반복 설명 문구를 따로 추출하지 못했습니다."

        top_notes = notes.value_counts().head(3)
        lines = [f"'{text}' 문구가 {count}회 보입니다." for text, count in top_notes.items()]
        return " ".join(lines)

    def available_function_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": "summarize_similar_logs",
                "description": "검색된 유사 로그의 건수, 주요 유형, 위험도, 파일 분포를 간단히 요약합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"},
                    },
                    "required": ["keyword"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "describe_repeated_features",
                "description": "유사 로그에서 반복되는 수치형 특징과 시간 범위를 설명합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "extract_note_patterns",
                "description": "note 컬럼에 기록된 반복 문구나 특징을 뽑아 설명합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "build_response_guide",
                "description": "검색 결과를 바탕으로 실무 점검 가이드를 제공합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
                "strict": True,
            },
        ]

    def run_function_call_interpretation(self, keyword: str, result_df: pd.DataFrame, stats: Dict[str, Any]) -> str:
        if self.client is None:
            raise RuntimeError("OPENAI_API_KEY가 없어 function calling 해석을 실행할 수 없습니다.")
        if result_df.empty:
            raise RuntimeError("검색 결과가 없어 AI 해석을 실행할 수 없습니다.")

        tool_impls: Dict[str, Callable[..., str]] = {
            "summarize_similar_logs": lambda keyword=keyword: self.summarize_similar_logs(keyword, stats),
            "describe_repeated_features": lambda: self.describe_repeated_features(stats),
            "extract_note_patterns": lambda: self.extract_note_patterns(result_df),
            "build_response_guide": lambda: self.build_response_guide(stats),
        }

        input_items = [
            {
                "role": "system",
                "content": (
                    "너는 보안 로그 분석 보조 도구다. "
                    "반드시 필요한 함수들을 먼저 호출한 뒤, "
                    "유사 로그가 얼마나 있었는지와 그 패턴이 어떤 의미인지 한국어로 설명한다. "
                    "과장하지 말고 사실과 추론을 구분한다. "
                    "또한 가능한 경우 MITRE ATT&CK 관점에서 technique_id, technique_name, tactic을 제시하라. "
                    "근거가 부족하면 확정하지 말고 후보라고 명시하라."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"검색어: {keyword}\n"
                    "질문: 이 로그와 비슷한 사례가 얼마나 있었는지, 반복되는 특징이 무엇인지, "
                    "왜 이상 패턴으로 볼 수 있는지 설명해줘.\n"
                    "가능하면 MITRE ATT&CK 기준으로도 해석해줘.\n"
                    f"참고 통계:\n{self._serialize_stats(stats)}"
                ),
            },
        ]

        response = self.client.responses.create(
            model="gpt-5",
            input=input_items,
            tools=self.available_function_tools(),
        )

        max_rounds = 3
        for _ in range(max_rounds):
            tool_outputs: List[Dict[str, Any]] = []

            for item in getattr(response, "output", []):
                if getattr(item, "type", "") != "function_call":
                    continue

                name = getattr(item, "name", "")
                call_id = getattr(item, "call_id", "")

                try:
                    args = json.loads(getattr(item, "arguments", "{}") or "{}")
                except json.JSONDecodeError:
                    args = {}

                if name not in tool_impls:
                    result = f"지원하지 않는 함수입니다: {name}"
                else:
                    try:
                        result = tool_impls[name](**args)
                    except TypeError:
                        result = tool_impls[name]()
                    except Exception as exc:
                        result = f"함수 실행 실패: {exc}"

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": result,
                    }
                )

            if not tool_outputs:
                break

            response = self.client.responses.create(
                model="gpt-5",
                previous_response_id=response.id,
                input=tool_outputs,
                tools=self.available_function_tools(),
            )

        return response.output_text

    # ---------- file search ----------
    def safe_name(self, text: str) -> str:
        safe = "".join(c for c in str(text) if c.isalnum() or c in ("_", "-")).strip()
        return safe or "search"

    def save_results(self, keyword: str, result_df: pd.DataFrame) -> str:
        csv_path = os.path.join(self.output_dir, f"{self.safe_name(keyword)}_results.csv")
        result_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        return csv_path

    def save_analysis_text(self, keyword: str, analysis_text: str) -> str:
        txt_path = os.path.join(self.output_dir, f"{self.safe_name(keyword)}_analysis.txt")
        with open(txt_path, "w", encoding="utf-8") as file:
            file.write(analysis_text)
        return txt_path

    def save_csv_analysis_to_db(
        self,
        keyword: str,
        result_df: pd.DataFrame,
        stats: Dict[str, Any],
        analysis_text: str,
        csv_path: str,
        session_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "session_id": session_id,
            "result_file_name": os.path.basename(csv_path),
            "query_text": keyword,
            "matched_rows_count": int(len(result_df)),
            "summary_text": json.dumps(stats, ensure_ascii=False, indent=2),
            "openai_analysis": analysis_text,
        }

        try:
            response = requests.post(
                self.fastapi_csv_api_url,
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            print(f"[CSV_ANALYSIS_DB_SAVE_ERROR] {exc}")
            return None

    def create_vector_store_with_file(self, csv_path: str, keyword: str) -> Tuple[str, str]:
        if self.client is None:
            raise RuntimeError("OPENAI_API_KEY가 없어 File Search를 실행할 수 없습니다.")

        with open(csv_path, "rb") as file:
            uploaded_file = self.client.files.create(file=file, purpose="user_data")

        vector_store = self.client.vector_stores.create(name=f"similar-log-{self.safe_name(keyword)}")
        batch = self.client.vector_stores.file_batches.create(
            vector_store_id=vector_store.id,
            file_ids=[uploaded_file.id],
        )

        for _ in range(15):
            current_batch = self.client.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store.id,
                batch_id=batch.id,
            )
            if current_batch.status == "completed":
                return vector_store.id, uploaded_file.id
            if current_batch.status in ("failed", "cancelled"):
                raise RuntimeError(f"파일 배치 처리 실패: {current_batch.status}")
            time.sleep(2)

        raise TimeoutError("vector store 파일 처리 시간이 너무 오래 걸립니다.")

    def analyze_with_file_search(self, keyword: str, stats: Dict[str, Any], vector_store_id: str) -> str:
        if self.client is None:
            raise RuntimeError("OPENAI_API_KEY가 없어 File Search를 실행할 수 없습니다.")

        prompt = f"""
사용자는 '{keyword}' 관련 유사 로그를 찾았습니다.

다음 형식으로 답변하세요.
- 유사 사례 요약
- 반복되는 특징
- 이상 패턴으로 볼 수 있는 이유
- 조심스럽게 추론 가능한 부분
- 추가 확인 항목

중요:
- file_search로 찾은 로그 내용에 근거해 설명할 것
- 과장하지 말고 사실과 추론을 구분할 것
- '근거 분석' 같은 표현보다 사용자가 이해하기 쉬운 문장으로 쓸 것

참고 통계:
{self._serialize_stats(stats)}
"""

        response = self.client.responses.create(
            model="gpt-5",
            input=prompt,
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id],
                    "max_num_results": 5,
                }
            ],
            include=["file_search_call.results"],
        )

        examples: List[str] = []
        for item in getattr(response, "output", []):
            if getattr(item, "type", "") != "file_search_call":
                continue
            for idx, result in enumerate(getattr(item, "results", []), start=1):
                filename = getattr(result, "filename", "unknown")
                text = getattr(result, "text", "")[:300]
                if text:
                    examples.append(f"{idx}. {filename}: {text}")

        if examples:
            return response.output_text + "\n\n[AI가 참고한 유사 로그]\n" + "\n".join(examples)
        return response.output_text

    def run_ai_interpretation(self, keyword: str, result_df: pd.DataFrame, stats: Dict[str, Any]) -> Dict[str, Any]:
        csv_path = self.save_results(keyword, result_df)
        function_call_text = self.run_function_call_interpretation(keyword, result_df, stats)
        vector_store_id, uploaded_file_id = self.create_vector_store_with_file(csv_path, keyword)
        file_search_text = self.analyze_with_file_search(keyword, stats, vector_store_id)

        combined = (
            "[유사 로그 요약 및 패턴 해석]\n"
          + function_call_text.strip()
            + "\n\n[유사 사례 AI 해석]\n"
            + file_search_text.strip()
        )

        txt_path = self.save_analysis_text(keyword, combined)

        db_save_result = self.save_csv_analysis_to_db(
            keyword=keyword,
            result_df=result_df,
            stats=stats,
            analysis_text=combined,
            csv_path=csv_path,
            session_id=None,
        )

        return {
            "csv_path": csv_path,
            "txt_path": txt_path,
            "uploaded_file_id": uploaded_file_id,
            "vector_store_id": vector_store_id,
            "analysis_text": combined,
            "db_save_result": db_save_result,
        }