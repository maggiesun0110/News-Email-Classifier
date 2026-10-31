import pandas as pd

df = pd.read_csv("new_labels.csv", dtype={"message_id": str, "thread_id": str})

print(df.shape)
print(df["label"].value_counts())
print(df["message_id"].duplicated().sum())

original = pd.read_csv("emails_copy.csv")

print("Original:", original.columns.tolist())
print("New:", df.columns.tolist())

import re

def sender_address(sender):
    match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", str(sender))
    return match.group(0).lower() if match else ""

df["sender_key"] = df["sender"].apply(sender_address)
original["sender_key"] = original["sender"].apply(sender_address)

match_columns = ["sender_key", "subject", "snippet"]
overlap = df.merge(
    original,
    on=match_columns,
    how="inner",
    suffixes=("_new", "_original")
)
print(df[["sender", "sender_key"]].head().to_string(index=False))
print(original[["sender", "sender_key"]].head().to_string(index=False))

possible_overlap = df.merge(
    original,
    on=["sender_key", "subject"],
    how="inner",
    suffixes=("_new", "_original")
)

print("Possible matches:", len(possible_overlap))
print(
    possible_overlap[
        ["subject", "label_new", "label_original"]
    ].to_string(index=False)
)

for _, row in possible_overlap.iterrows():
    print("\nSubject:", row["subject"])
    print("New snippet:", row["snippet_new"])
    print("Original snippet:", row["snippet_original"])

columns = [
    "message_id", "thread_id",
    "sender", "subject", "snippet", "label"
]

combined = pd.concat(
    [original.reindex(columns=columns), df[columns]],
    ignore_index=True
)

print(combined.shape)
print(combined["label"].value_counts()) 

groups = combined["thread_id"].copy()
missing_threads = groups.isna()

groups.loc[missing_threads] = [
    f"original_{i}" for i in groups.index[missing_threads]
]

combined["group_id"] = groups
combined.to_csv("combined_emails-341.csv", index=False)
print("Missing groups:", combined["group_id"].isna().sum())
print("Unique groups:", combined["group_id"].nunique())
