
import joblib
import pandas as pd

from pathlib import Path

# Find project folder
PROJECT_FOLDER = Path(__file__).resolve().parent.parent

# Load saved model
MODEL_PATH = PROJECT_FOLDER / "ml_model" / "student_model.pkl"

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
features = model_data["features"]

# Example student information
student_data = pd.DataFrame(
    [[5, 85, 75, 7]],
    columns=features
)

# Predict exam score
predicted_score = model.predict(student_data)

print("SMARTSTUDY AI - STUDENT PERFORMANCE PREDICTION")
print("----------------------------------------------")
print("Study Hours: 5")
print("Attendance: 85%")
print("Previous Marks: 75")
print("Sleep Hours: 7")
print("----------------------------------------------")
print("Predicted Exam Score:", round(float(predicted_score[0]), 2))
