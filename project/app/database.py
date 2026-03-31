# SQLAlchemy DB 연결 및 세션 관리 설정

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# DB 접속 URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# 환경 변수 누락 시 실행 중단 (초기 설정 오류 방지)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL이 .env 파일에 설정되지 않았습니다.")

# DB 엔진 생성 (echo=True → SQL 로그 출력, 디버깅용)
engine = create_engine(DATABASE_URL, echo=True)

# 세션 생성기 설정
# autocommit=False → 명시적으로 commit 필요
# autoflush=False → 필요할 때만 flush
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 모델의 기본 클래스 (모든 모델이 상속)
Base = declarative_base()


# FastAPI에서 사용하는 DB 세션 의존성 함수
def get_db():
    db = SessionLocal()  # 세션 생성
    try:
        yield db         # 요청 동안 DB 세션 제공
    finally:
        db.close()       # 요청 종료 시 세션 종료 (자원 누수 방지)