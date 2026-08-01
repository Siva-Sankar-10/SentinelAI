import pandas as pd

# Load dataset
df = pd.read_csv("dataset/KDDTrain+.txt", header=None)

print("Dataset Loaded Successfully!")
print("Rows and Columns:", df.shape)

print("\nFirst 5 Rows:")
print(df.head())