import os
import pandas as pd
import joblib
from tensorflow import keras
from sklearn.preprocessing import StandardScaler

from ml.serving.preprocessor import CyberPreprocessor
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras import regularizers

def train_cyber_model():
    # Load the dataset
    print("Loading data...")
    data = pd.read_csv("data.csv")
    print(f"Data shape: {data.shape}")

    # Target and feature selection
    if "Label" not in data.columns:
        raise ValueError("Missing 'Label' column in dataset.")
    
    selected_features = [
        'Flow Duration', 'Total Fwd Packet', 'Total Bwd Packets',
        'Fwd Packets/s', 'Bwd Packets/s', 'Flow Packets/s',
        'Fwd Header Length', 'Bwd Header Length',
        'Fwd Packet Length Mean', 'Bwd Packet Length Mean',
        'Packet Length Mean', 'Packet Length Std',
        'Flow IAT Mean', 'Flow IAT Std',
        'Active Mean', 'Idle Mean',
        'FWD Init Win Bytes', 'Bwd Init Win Bytes'
    ]

    # Drop rows with missing selected columns
    data = data.dropna(subset=selected_features + ["Label"])

    X = data[selected_features]
    y = data["Label"]

    # Preprocessing
    preprocessor = CyberPreprocessor()
    X_processed = preprocessor.fit_transform(X)

    # Build and train model
    print("Building model...")
    model = keras.Sequential([
        keras.layers.Dense(64, activation="relu", input_shape=(X_processed.shape[1],)),
        keras.layers.Dropout(0.5),  # Dropout added
        keras.layers.Dense(32, activation="relu", kernel_regularizer=regularizers.l2(0.01)),  # L2 Regularization
        keras.layers.Dropout(0.5),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    # Early stopping and learning rate scheduler
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-6)

    # Training with callbacks
    print("Starting model training...")
    history = model.fit(X_processed, y, epochs=10, batch_size=32, validation_split=0.2, 
                        callbacks=[early_stopping, lr_scheduler])
    print("Model training finished.")

    # Print training history
    print("Training history:", history.history)

    # Save model and preprocessor
    os.makedirs("model_storage", exist_ok=True)
    joblib.dump(preprocessor, "model_storage/preprocessor.joblib")
    model.save("model_storage/model.keras")
    print("✅ Model and preprocessor saved.")

if __name__ == "__main__":
    train_cyber_model()
