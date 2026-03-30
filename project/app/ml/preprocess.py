import pandas as pd

FEATURE_COLUMNS = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Mean",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Flow IAT Mean",
    "Packet Length Mean",
    "Init Fwd Win Bytes"
]

def make_model_input(input_features_json: dict) -> pd.DataFrame:
    missing = [col for col in FEATURE_COLUMNS if col not in input_features_json]
    if missing:
        raise ValueError(f"필수 피처 누락: {missing}")

    row = {}
    for col in FEATURE_COLUMNS:
        row[col] = float(input_features_json[col])

    df = pd.DataFrame([row], columns=FEATURE_COLUMNS)
    return df