from pathlib import Path
import json

import numpy as np
import pandas as pd


RAW_DIR = Path("data")
OUT_DIR = Path("data/processed")
OUT_FILE = OUT_DIR / "csecicids2018_model_ready.csv"
SUMMARY_FILE = OUT_DIR / "csecicids2018_summary.json"

# Map dataset columns to the exact feature names expected by the current trainer.
COLUMN_MAP = {
    "Total Fwd Packets": "Total Fwd Packet",
    "Total Backward Packets": "Total Bwd Packets",
    "Init Fwd Win Bytes": "FWD Init Win Bytes",
    "Init Bwd Win Bytes": "Bwd Init Win Bytes",
}

SELECTED_FEATURES = [
    "Flow Duration",
    "Total Fwd Packet",
    "Total Bwd Packets",
    "Fwd Packets/s",
    "Bwd Packets/s",
    "Flow Packets/s",
    "Fwd Header Length",
    "Bwd Header Length",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Mean",
    "Packet Length Mean",
    "Packet Length Std",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Active Mean",
    "Idle Mean",
    "FWD Init Win Bytes",
    "Bwd Init Win Bytes",
]


def to_binary_label(value: object) -> int:
    text = str(value).strip().lower()
    return 0 if text == "benign" else 1


def main() -> None:
    files = sorted(RAW_DIR.glob("*.parquet"))
    if not files:
        raise FileNotFoundError("No parquet files found in data/")

    frames = []
    for file_path in files:
        df = pd.read_parquet(file_path)
        df = df.rename(columns=COLUMN_MAP)

        required = SELECTED_FEATURES + ["Label"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in {file_path.name}: {missing}")

        sliced = df[required].copy()
        frames.append(sliced)

    merged = pd.concat(frames, ignore_index=True)
    rows_before = len(merged)

    merged = merged.replace([np.inf, -np.inf], np.nan)
    merged = merged.dropna(subset=SELECTED_FEATURES + ["Label"])

    for feature in SELECTED_FEATURES:
        merged[feature] = pd.to_numeric(merged[feature], errors="coerce")

    merged = merged.dropna(subset=SELECTED_FEATURES)
    merged["Label"] = merged["Label"].map(to_binary_label).astype(int)

    rows_after = len(merged)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT_FILE, index=False)

    summary = {
        "source_files": [p.name for p in files],
        "rows_before_cleaning": rows_before,
        "rows_after_cleaning": rows_after,
        "dropped_rows": rows_before - rows_after,
        "columns": merged.columns.tolist(),
        "label_distribution": merged["Label"].value_counts().to_dict(),
        "output_file": str(OUT_FILE),
    }

    SUMMARY_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
