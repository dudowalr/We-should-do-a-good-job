import pandas as pd
from pathlib import Path

file_path = Path(r"D:\sk쉴더스\project\module1\cic-collection.parquet")
output_path = file_path.with_name("classlabel_label_samples_2each.csv")

target_class_labels = [
    "Botnet",
    "Bruteforce",
    "DDoS",
    "DoS",
    "Infiltration",
    "Portscan",
    "Webattack",
]

feature_cols = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Mean",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Flow IAT Mean",
    "Packet Length Mean",
    "Init Fwd Win Bytes",
]

if not file_path.exists():
    raise FileNotFoundError(f"파일이 없습니다: {file_path}")

df = pd.read_parquet(file_path)

required_cols = ["ClassLabel", "Label"] + feature_cols
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"다음 컬럼이 없습니다: {missing_cols}")

df["ClassLabel"] = df["ClassLabel"].astype(str).str.strip()
df["Label"] = df["Label"].astype(str).str.strip()

df = df[df["ClassLabel"].isin(target_class_labels)].copy()
df = df[df["ClassLabel"] != "Benign"].copy()
df = df.dropna(subset=feature_cols)

result_frames = []

for class_name in target_class_labels:
    class_df = df[df["ClassLabel"] == class_name].copy()

    label_counts = class_df["Label"].value_counts()
    valid_labels = label_counts[label_counts >= 2].index.tolist()

    if len(valid_labels) < 2:
        continue

    class_df = class_df[class_df["Label"].isin(valid_labels)].copy()

    for label_name in sorted(class_df["Label"].unique().tolist()):
        temp = class_df[class_df["Label"] == label_name].head(2).copy()
        result_frames.append(temp[["ClassLabel", "Label"] + feature_cols])

if not result_frames:
    raise ValueError("조건에 맞는 데이터가 없습니다.")

result_df = pd.concat(result_frames, ignore_index=True)

result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("저장 완료:", output_path)
print()
print("추출 결과 개수:")
print(result_df.groupby(["ClassLabel", "Label"]).size())
print()
print("총 행 개수:", len(result_df))
print("총 컬럼 개수:", len(result_df.columns))