
import pandas as pd

df = pd.read_csv("beat_saber_ml_dataset.csv")

# Find all rows sharing the same recording, time and label
duplicates = df[
    df.duplicated(
        subset=["recording_id", "event_time", "label"],
        keep=False
    )
].copy()

print("Rows belonging to duplicate groups:", len(duplicates))

print("\nDuplicate groups by label:")
print(duplicates.groupby("label").size())

print("\nExample duplicate rows:")
print(
    duplicates[
        ["recording_id", "event_time", "label"]
    ].head(20).to_string(index=False)
)

print("\nUnique duplicate groups:")
print(
    duplicates.groupby(
        ["recording_id", "event_time", "label"]
    ).size().value_counts()
)

# Check whether feature vectors are identical
feature_cols = [
    col for col in df.columns
    if col not in ["recording_id", "event_time", "label"]
]

print("\nCompletely identical rows:")
print(df.duplicated().sum())

print("\nIdentical feature vectors:")
print(df.duplicated(subset=feature_cols).sum())
