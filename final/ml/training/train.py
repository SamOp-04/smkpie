import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from ml.serving.preprocessor import CyberPreprocessor


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


class CyberMLP(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.network(x)


def load_dataset(data_path: Path, max_rows: int | None, random_state: int) -> pd.DataFrame:
    df = pd.read_csv(data_path)
    required_columns = SELECTED_FEATURES + ["Label"]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")

    df = df[required_columns].replace([np.inf, -np.inf], np.nan).dropna()
    if max_rows and max_rows < len(df):
        df = df.sample(n=max_rows, random_state=random_state)
    df["Label"] = df["Label"].astype(int)
    return df


def build_dataloaders(X_train, y_train, X_test, y_test, batch_size: int):
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32).unsqueeze(1),
    )
    test_dataset = TensorDataset(
        torch.tensor(X_test, dtype=torch.float32),
        torch.tensor(y_test, dtype=torch.float32).unsqueeze(1),
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader


def evaluate_model(model, data_loader, device):
    model.eval()
    probs = []
    labels = []

    with torch.no_grad():
        for features, targets in data_loader:
            features = features.to(device)
            logits = model(features)
            batch_probs = torch.sigmoid(logits).cpu().numpy().ravel()
            probs.extend(batch_probs.tolist())
            labels.extend(targets.numpy().ravel().tolist())

    y_true = np.array(labels, dtype=int)
    y_prob = np.array(probs, dtype=float)
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.0,
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
    return metrics


def train_cyber_model(
    data_path: str = "data/processed/csecicids2018_model_ready.csv",
    epochs: int = 5,
    batch_size: int = 4096,
    learning_rate: float = 1e-3,
    test_size: float = 0.2,
    max_rows: int | None = 1_000_000,
    random_state: int = 42,
):
    dataset_path = Path(data_path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    print(f"Loading dataset from {dataset_path}...")
    df = load_dataset(dataset_path, max_rows=max_rows, random_state=random_state)
    print(f"Rows used for training: {len(df)}")

    X = df[SELECTED_FEATURES]
    y = df["Label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    preprocessor = CyberPreprocessor()
    X_train_scaled = preprocessor.fit_transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)

    train_loader, test_loader = build_dataloaders(
        X_train_scaled,
        y_train.to_numpy(),
        X_test_scaled,
        y_test.to_numpy(),
        batch_size=batch_size,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = CyberMLP(input_dim=X_train_scaled.shape[1]).to(device)
    pos_ratio = float((y_train == 0).sum()) / max(float((y_train == 1).sum()), 1.0)
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_ratio], device=device))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        for features, targets in train_loader:
            features = features.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            logits = model(features)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item())

        avg_loss = epoch_loss / max(len(train_loader), 1)
        print(f"Epoch {epoch}/{epochs} - train_loss={avg_loss:.6f}")

    metrics = evaluate_model(model, test_loader, device)
    print("Evaluation metrics:")
    print(json.dumps(metrics, indent=2))

    output_dir = Path("model_storage")
    output_dir.mkdir(parents=True, exist_ok=True)

    torch.save(
        {
            "state_dict": model.state_dict(),
            "input_dim": X_train_scaled.shape[1],
            "features": SELECTED_FEATURES,
        },
        output_dir / "model.pt",
    )
    preprocessor.save(str(output_dir / "preprocessor.joblib"))

    with open(output_dir / "evaluation_metrics.json", "w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2)

    print(f"Saved model to {output_dir / 'model.pt'}")
    print(f"Saved metrics to {output_dir / 'evaluation_metrics.json'}")
    return metrics


def parse_args():
    parser = argparse.ArgumentParser(description="Train cyber anomaly model with PyTorch")
    parser.add_argument("--data-path", default="data/processed/csecicids2018_model_ready.csv")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--max-rows", type=int, default=1_000_000)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train_cyber_model(
        data_path=args.data_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        test_size=args.test_size,
        max_rows=args.max_rows,
        random_state=args.random_state,
    )
