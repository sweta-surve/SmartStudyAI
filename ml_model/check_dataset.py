import pandas as pd

data = pd.read_csv("dataset/StudentPerformanceFactors.csv")

print("FIRST FIVE STUDENT RECORDS")
print(data.head())

print("\nDATASET SHAPE")
print(data.shape)

print("\nCOLUMN NAMES")
print(data.columns.tolist())

print("\nMISSING VALUES")
print(data.isnull().sum())

print("\nDATASET SUMMARY")
print(data.describe())