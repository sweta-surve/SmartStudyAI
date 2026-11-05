
import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Project paths
PROJECT_FOLDER = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_FOLDER / "dataset" / "StudentPerformanceFactors.csv"
MODEL_PATH = PROJECT_FOLDER / "ml_model" / "student_model.pkl"

# Input features
FEATURES = [
    "Hours_Studied",
    "Attendance",
    "Previous_Scores",
    "Sleep_Hours"
]

# Prediction target
TARGET = "Exam_Score"


def train_model():

    print("Loading student dataset...")

    # Step 1: Load dataset
    data = pd.read_csv(DATASET_PATH)

    print("Original dataset shape:", data.shape)

    # Step 2: Select required columns
    required_columns = FEATURES + [TARGET]
    data = data[required_columns].copy()

    # Step 3: Convert columns to numeric
    for column in required_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Step 4: Remove missing values
    data = data.dropna()

    print("Dataset after cleaning:", data.shape)

    # Step 5: Remove invalid exam scores
    unusual_scores = data[
        (data[TARGET] < 0) | (data[TARGET] > 100)
    ]

    print("Invalid exam scores found:", len(unusual_scores))

    data = data[
        (data[TARGET] >= 0) & (data[TARGET] <= 100)
    ].copy()

    print("Dataset after removing invalid scores:", data.shape)

    # Step 6: Separate inputs and output
    X = data[FEATURES]
    y = data[TARGET]

    # Step 7: Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    print("Training records:", len(X_train))
    print("Testing records:", len(X_test))

    # Step 8: Create model
    model = LinearRegression()

    # Step 9: Train model
    print("\nTraining the model...")

    model.fit(X_train, y_train)

    # Step 10: Make predictions
    predictions = model.predict(X_test)

    # Step 11: Evaluate model
    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    rmse = mse ** 0.5
    r2 = r2_score(y_test, predictions)

    print("\nMODEL EVALUATION")
    print("-------------------------")
    print("MAE:", round(mae, 2))
    print("RMSE:", round(rmse, 2))
    print("R2 Score:", round(r2, 4))

    # Step 12: Save trained model
    model_data = {
        "model": model,
        "features": FEATURES
    }

    joblib.dump(model_data, MODEL_PATH)

    print("\nModel saved successfully!")
    print("Saved location:", MODEL_PATH)


if __name__ == "__main__":
    train_model()
