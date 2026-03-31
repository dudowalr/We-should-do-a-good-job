import pandas as pd
from pathlib import Path

base = Path.cwd()
candidates = [
    base / "cic-collection.parquet",
    base / "module1" / "cic-collection.parquet",
    base / "project" / "module1" / "cic-collection.parquet",
]

file_path = next((p for p in candidates if p.exists()), None)
if file_path is None:
    raise FileNotFoundError("cic-collection.parquet 파일을 찾을 수 없습니다.")

df = pd.read_parquet(file_path)

col_map = {str(col).strip().lower(): col for col in df.columns}

label_col = None
class_label_col = None

for key, original in col_map.items():
    if key == "label":
        label_col = original
    if key in {"class label", "class_label", "classlabel"}:
        class_label_col = original

if label_col is None or class_label_col is None:
    raise KeyError(f"필요한 컬럼을 찾지 못했습니다. 현재 컬럼: {list(df.columns)}")

result = df[[label_col, class_label_col]].copy()

mask = (
    result[label_col].astype(str).str.strip().str.lower().ne("benign") &
    result[class_label_col].astype(str).str.strip().str.lower().ne("benign")
)

result = result[mask].drop_duplicates().reset_index(drop=True)

out_path = file_path.with_name("cic_labels_without_benign.csv")
result.to_csv(out_path, index=False, encoding="utf-8-sig")

print(result)
print(f"\n저장 완료: {out_path}")