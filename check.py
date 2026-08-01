import pandas as pd

df = pd.read_csv("dataset/KDDTrain+.txt", header=None)

print(df.shape)
print(df.head())