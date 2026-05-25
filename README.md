# 프로젝트 실행 가이드 

이 문서는 **최신 `project` 폴더를 clone 해온 상태**를 기준으로 작성되었습니다.
업로드된 가이드 문서의 설치·실행 절차를 README 형식으로 정리한 것입니다. 

## 1. 실행 전 준비 사항

아래 항목이 필요합니다.

- Python 가상환경
- MySQL 8.0.45
- `requirements.txt`에 있는 패키지
- 별도로 제공되는 모델 파일(`.pkl`)
- OpenAI API Key

---

## 2. MySQL 설치 및 DB 생성

가이드에서는 **MySQL Installer 8.0.45** 설치를 기준으로 안내하고 있습니다. 설치 후 `root` 비밀번호는 기억해 두었다가 `.env` 파일에 입력해야 합니다.

### 2-1. DB 생성

MySQL 실행 후 아래 SQL을 순서대로 실행합니다.

```sql
CREATE DATABASE project_db;
USE project_db;
```

### 2-2. 테이블 생성

```sql
CREATE TABLE incident_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NULL,
    input_features_json JSON NOT NULL,
    predicted_label VARCHAR(100) NULL,
    confidence_score FLOAT NULL,
    kill_chain_stage VARCHAR(255) NULL,
    defense_mechanism TEXT NULL,
    llm_recommendation TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
ALTER TABLE incident_logs
ADD COLUMN risk_level VARCHAR(50) NULL,
ADD COLUMN anomaly_summary TEXT NULL;
```

```sql
CREATE TABLE threat_intelligence (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    kill_chain_stage VARCHAR(255) NOT NULL,
    defense_mechanism TEXT NOT NULL,
    recommendation_text TEXT NULL,
    reference_source VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
CREATE TABLE csv_analysis_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NULL,
    result_file_name VARCHAR(255) NULL,
    query_text TEXT NULL,
    matched_rows_count INT NULL,
    summary_text LONGTEXT NULL,
    openai_analysis LONGTEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
CREATE TABLE user_feedback (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    incident_log_id BIGINT NOT NULL,
    rating INT NULL,
    feedback_text TEXT NULL,
    is_helpful BOOLEAN NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_incident
        FOREIGN KEY (incident_log_id) REFERENCES incident_logs(id)
        ON DELETE CASCADE
);
```

---

## 3. 가상환경 생성 및 활성화

`project` 폴더를 VS Code로 연 뒤 가상환경을 생성합니다. 가이드에는 `requirements.txt`를 선택한 상태로 가상환경을 만들고, 이후 아래 명령어로 활성화하도록 되어 있습니다. 

```bash
source .venv/Scripts/activate
```

> Windows 환경 기준 명령어입니다.

---

## 4. 모델 파일(.pkl) 추가

가이드에 따르면 모델 파일은 용량 문제로 GitHub에 포함되지 않았으므로 **별도로 받아서 추가**해야 합니다. 

다음 구조로 넣어주세요.

```text
project/
├─ model_files/
│  ├─ hybrid_step1_binary.pkl
│  └─ hybrid_step2_multi.pkl
```

---

## 5. `.env` 파일 생성

`project` 바로 아래에 `.env` 파일을 생성합니다. 가이드의 예시는 아래와 같습니다.

```env
DATABASE_URL=mysql+pymysql://root:비밀번호@localhost:3306/project_db
OPENAI_API_KEY=여기에_키_입력
FASTAPI_CSV_API_URL=
FASTAPI_PREDICT_API_URL=
FASTAPI_FEEDBACK_API_URL=
```

파일 위치는 아래와 같습니다.

```text
project/
├─ .env
```

---

## 6. 패키지 설치

가상환경을 활성화한 뒤 아래 명령어를 실행합니다. 

```bash
pip install -r requirements.txt
```

---

## 7. 실행 방법

가이드에서는 **터미널 2개를 열어서 각각 실행**하도록 안내하고 있습니다. 순서대로 실행하면 됩니다. 

### 터미널 1: FastAPI 서버 실행

```bash
uvicorn app.main:app --reload
```

### 터미널 2: Streamlit 실행

```bash
streamlit run frontend/main.py
```

처음 Streamlit을 실행하면 이메일 입력 안내가 나올 수 있습니다. 가이드에는 한 번 입력하라고 되어 있습니다. 

---

## 8. 폴더 구조 예시

```text
project/
├─ .env
├─ model_files/
│  ├─ hybrid_step1_binary.pkl
│  └─ hybrid_step2_multi.pkl
├─ app/
├─ frontend/
├─ requirements.txt
```

---

## 9. 체크리스트

실행 전 아래 항목을 확인하세요.

- [ ] MySQL 설치 완료
- [ ] `project_db` 생성 완료
- [ ] 테이블 생성 완료
- [ ] `.venv` 생성 및 활성화 완료
- [ ] `requirements.txt` 설치 완료
- [ ] `.env` 파일 작성 완료
- [ ] `model_files` 폴더에 `.pkl` 2개 추가 완료
- [ ] FastAPI 서버 실행 완료
- [ ] Streamlit 실행 완료

---

## 10. 실행이 안 될 때 먼저 확인할 것

1. MySQL이 실행 중인지 확인
2. `.env`의 `DATABASE_URL` 비밀번호가 맞는지 확인
3. `.pkl` 파일 2개가 정확한 경로에 있는지 확인
4. 가상환경이 활성화된 상태인지 확인
5. `pip install -r requirements.txt`를 정상적으로 수행했는지 확인

---

## 11. 한 줄 요약

이 프로젝트는 다음 순서로 준비하면 됩니다.

**MySQL 설치 → DB 및 테이블 생성 → 가상환경 생성 → `.pkl` 파일 추가 → `.env` 작성 → 패키지 설치 → FastAPI 실행 → Streamlit 실행**
