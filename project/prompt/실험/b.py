from pathlib import Path
import pandas as pd

base_dir = Path(__file__).resolve().parent

benign_path = base_dir / "sample.csv"
attack_candidates = [
    base_dir / "cic_non_benign.csv",
    base_dir / "filtered_non_benign.csv",
    base_dir / "cic-collection.parquet",
    base_dir / "prompt_test_from_realdata.csv",
]

mapping_candidates = [
    base_dir / "attack_prompt_mapping.csv",
    base_dir / "attack_labels_only.csv",
]

def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)

def norm_text(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip()

def build_label_key(df: pd.DataFrame) -> pd.Series:
    if "ClassLabel" in df.columns:
        s = norm_text(df["ClassLabel"])
        if not s.eq("").all():
            return s.str.lower()
    if "Label" in df.columns:
        return norm_text(df["Label"]).str.lower()
    raise ValueError("Label 또는 ClassLabel 컬럼이 없습니다.")

def ensure_label_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Label" not in out.columns and "ClassLabel" in out.columns:
        out["Label"] = out["ClassLabel"]
    if "ClassLabel" not in out.columns and "Label" in out.columns:
        out["ClassLabel"] = out["Label"]
    return out

if not benign_path.exists():
    raise FileNotFoundError(f"sample.csv 파일이 없습니다: {benign_path}")

benign_df = ensure_label_columns(load_table(benign_path))
benign_key = build_label_key(benign_df)
benign_df = benign_df[benign_key.eq("benign")].copy()

attack_path = next((p for p in attack_candidates if p.exists()), None)
if attack_path is None:
    raise FileNotFoundError("공격 데이터 파일을 찾을 수 없습니다. cic_non_benign.csv / filtered_non_benign.csv / cic-collection.parquet / prompt_test_from_realdata.csv 중 하나가 필요합니다.")

attack_df = ensure_label_columns(load_table(attack_path))
attack_key = build_label_key(attack_df)
attack_df = attack_df[~attack_key.eq("benign")].copy()

merged_df = pd.concat([benign_df, attack_df], ignore_index=True)
merged_df = ensure_label_columns(merged_df)

mapping_frames = []
for path in mapping_candidates:
    if path.exists():
        m = load_table(path).copy()
        if "ClassLabel" not in m.columns and "Label" not in m.columns:
            continue
        m = ensure_label_columns(m)
        m["__merge_key__"] = build_label_key(m)
        m = m.drop_duplicates(subset="__merge_key__")
        mapping_frames.append(m)

merged_df["__merge_key__"] = build_label_key(merged_df)

for i, m in enumerate(mapping_frames, start=1):
    extra_cols = [c for c in m.columns if c not in {"Label", "ClassLabel", "__merge_key__"}]
    if extra_cols:
        merged_df = merged_df.merge(
            m[["__merge_key__"] + extra_cols],
            on="__merge_key__",
            how="left",
            suffixes=("", f"_map{i}")
        )

drop_cols = [c for c in merged_df.columns if c == "__merge_key__" or c.startswith("Unnamed:")]
merged_df = merged_df.drop(columns=drop_cols, errors="ignore")
merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()].copy()
merged_df = merged_df.dropna(axis=1, how="all")
merged_df = merged_df.drop_duplicates().reset_index(drop=True)

output_path = base_dir / "cic_project_merged.csv"
merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"benign rows: {len(benign_df)}")
print(f"attack rows: {len(attack_df)}")
print(f"merged rows: {len(merged_df)}")
print(f"saved to: {output_path}")
print(merged_df["ClassLabel"].value_counts(dropna=False))