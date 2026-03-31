from sqlalchemy import Column, BigInteger, String, Float, Text, TIMESTAMP, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


# 예측 요청 및 분석 결과 저장 테이블
class IncidentLog(Base):
    __tablename__ = "incident_logs"

    feedbacks = relationship("UserFeedback", backref="incident", passive_deletes=True)

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), nullable=True)
    input_features_json = Column(JSON, nullable=False)
    predicted_label = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)
    kill_chain_stage = Column(String(255), nullable=True)
    defense_mechanism = Column(Text, nullable=True)
    llm_recommendation = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


# 위협 인텔리전스 기준 정보 저장 테이블
class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    label = Column(String(100), nullable=False)
    kill_chain_stage = Column(String(255), nullable=False)
    defense_mechanism = Column(Text, nullable=False)
    recommendation_text = Column(Text, nullable=True)
    reference_source = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


# 사용자 피드백 저장 테이블
class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    incident_log_id = Column(BigInteger, ForeignKey("incident_logs.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=True)
    feedback_text = Column(Text, nullable=True)
    is_helpful = Column(Boolean, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


# CSV 분석 결과 로그 저장 테이블
class CsvAnalysisLog(Base):
    __tablename__ = "csv_analysis_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), nullable=True)
    result_file_name = Column(String(255), nullable=True)
    query_text = Column(Text, nullable=True)
    matched_rows_count = Column(Integer, nullable=True)
    summary_text = Column(LONGTEXT, nullable=True)
    openai_analysis = Column(LONGTEXT, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())