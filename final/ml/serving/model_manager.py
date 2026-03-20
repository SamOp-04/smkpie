import os
import logging
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import torch
from torch import nn
from core.config import settings


class _InferenceMLP(nn.Module):
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

class ModelManager:
    def __init__(self, base_path="model_storage"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        
    @property
    def model_path(self):
        return os.path.join(self.base_path, "model.pt")
    
    @property
    def preprocessor_path(self):
        return os.path.join(self.base_path, "preprocessor.joblib")

    def load_assets(self):
        """Load both model and preprocessor"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        if not os.path.exists(self.preprocessor_path):
            raise FileNotFoundError(f"Preprocessor not found at {self.preprocessor_path}")

        from ml.serving.preprocessor import CyberPreprocessor

        checkpoint = torch.load(self.model_path, map_location="cpu")
        input_dim = int(checkpoint.get("input_dim", 18))

        model = _InferenceMLP(input_dim)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()

        preprocessor = CyberPreprocessor.load(self.preprocessor_path)
        return model, preprocessor

    def save_assets(self, model, preprocessor):
        """Save both model and preprocessor"""
        input_dim = model[0].in_features if hasattr(model, "__getitem__") else 18
        torch.save({"state_dict": model.state_dict(), "input_dim": input_dim}, self.model_path)
        preprocessor.save(self.preprocessor_path)
        logging.info(f"Model assets saved to {self.base_path}")

    def update_model_version(self, source_path: str):
        """Replace current serving assets from a local path containing model.pt and preprocessor.joblib."""
        if source_path.startswith("s3://"):
            self._update_from_s3(source_path)
            logging.info("Model assets updated from %s", source_path)
            return

        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")

        if src.is_dir():
            model_src = src / "model.pt"
            pre_src = src / "preprocessor.joblib"
        else:
            if src.name != "model.pt":
                raise ValueError("Source file must be model.pt or a directory containing model.pt and preprocessor.joblib")
            model_src = src
            pre_src = Path(self.preprocessor_path)

        if not model_src.exists():
            raise FileNotFoundError(f"model.pt not found in source: {model_src}")
        if not pre_src.exists() and src.is_dir():
            raise FileNotFoundError(f"preprocessor.joblib not found in source: {pre_src}")

        if os.path.abspath(str(model_src)) != os.path.abspath(self.model_path):
            shutil.copy2(model_src, self.model_path)
        if src.is_dir():
            if os.path.abspath(str(pre_src)) != os.path.abspath(self.preprocessor_path):
                shutil.copy2(pre_src, self.preprocessor_path)

        logging.info("Model assets updated from %s", source_path)

    def _update_from_s3(self, s3_path: str):
        try:
            import boto3
        except ModuleNotFoundError as exc:
            raise RuntimeError("boto3 is required for S3 model sync") from exc

        prefix = s3_path.replace("s3://", "", 1)
        if "/" in prefix:
            bucket, key_prefix = prefix.split("/", 1)
        else:
            bucket = settings.S3_BUCKET
            key_prefix = prefix

        if not bucket:
            bucket = settings.S3_BUCKET
        if not bucket:
            raise ValueError("S3 bucket is required for model update")

        key_prefix = key_prefix.strip("/")
        model_key = f"{key_prefix}/model.pt" if key_prefix else "model.pt"
        preprocessor_key = f"{key_prefix}/preprocessor.joblib" if key_prefix else "preprocessor.joblib"

        client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        with TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            model_tmp = tmp_dir / "model.pt"
            preprocessor_tmp = tmp_dir / "preprocessor.joblib"

            try:
                client.download_file(bucket, model_key, str(model_tmp))
                client.download_file(bucket, preprocessor_key, str(preprocessor_tmp))
            except Exception as exc:
                raise RuntimeError(f"Failed to download model assets from s3://{bucket}/{key_prefix}") from exc

            shutil.copy2(model_tmp, self.model_path)
            shutil.copy2(preprocessor_tmp, self.preprocessor_path)