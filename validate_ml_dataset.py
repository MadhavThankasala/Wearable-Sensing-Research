
import pandas as pd
import numpy as np

df = pd.read_csv("beat_saber_ml_dataset.csv")

print("Dataset shape:", df.shape)

print("\nLabel distribution:")
print(df["label"].value_counts())

print("\nMissing values:")
print(df.isnull().sum()[df.isnull().sum() > 0])

numeric_cols = df.select_dtypes(include="number").columns

print("\nInfinite values:")
print(np.isinf(df[numeric_cols]).sum().sum())

print("\nNumber of recordings:")
print(df["recording_id"].nunique())

print("\nWindow frame count:")
print(df["window_frame_count"].describe())

print("\nDuplicate recording/event/label rows:")
print(df.duplicated(
    subset=["recording_id", "event_time", "label"]
).sum())

print("\nFeature statistics:")
print(df[[
    "head_avg_speed",
    "left_avg_speed",
    "right_avg_speed"
]].describe())
