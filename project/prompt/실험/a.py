import pandas as pd

# 1. 원본 parquet 읽기
df = pd.read_parquet("cic-collection.parquet")

# 2. 컬럼명 정리
df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()

print("컬럼 목록:")
print(df.columns.tolist())
print()

print("ClassLabel 분포:")
print(df["ClassLabel"].value_counts())
print()

# 3. 각 상위 공격군(ClassLabel)에서 2개씩 샘플 추출
#   - Benign 포함 8개 전부
sample_n = 2

sample_df = (
    df.groupby("ClassLabel", group_keys=False)
      .sample(n=sample_n, random_state=42)
      .reset_index(drop=True)
)

# 4. 확인
print("샘플 추출 결과:")
print(sample_df[["ClassLabel", "Label"]])
print()
print(sample_df["ClassLabel"].value_counts())
print()

# 5. 프롬프트 테스트용으로 핵심 컬럼만 따로 저장
prompt_df = sample_df[
    [
        "ClassLabel",
        "Label",
        "Flow Duration",
        "Total Fwd Packets",
        "Total Backward Packets",
        "Flow Bytes/s",
        "Flow Packets/s",
        "Packet Length Mean",
        "Packet Length Std",
        "SYN Flag Count",
        "Active Mean",
        "Idle Mean",
    ]
].copy()

prompt_df.to_csv("prompt_test_from_realdata.csv", index=False, encoding="utf-8-sig")
print("prompt_test_from_realdata.csv 저장 완료")
print()
print(prompt_df)