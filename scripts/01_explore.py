"""Profile the raw Superstore dataset: shape, types, nulls, ranges, cardinality."""
import pandas as pd

df = pd.read_csv("data/raw/Sample - Superstore.csv", encoding="latin1")

print("=== SHAPE ===")
print(df.shape)

print("\n=== DTYPES ===")
print(df.dtypes)

print("\n=== NULL COUNTS ===")
print(df.isnull().sum())

print("\n=== DUPLICATE ROWS ===")
print(df.duplicated().sum())

df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

print("\n=== DATE RANGE ===")
print("Order Date:", df["Order Date"].min(), "to", df["Order Date"].max())
print("Ship Date:", df["Ship Date"].min(), "to", df["Ship Date"].max())

print("\n=== CATEGORICAL CARDINALITY ===")
for col in ["Ship Mode", "Segment", "Region", "Category", "Sub-Category", "State", "City", "Customer Name", "Product Name"]:
    print(f"{col}: {df[col].nunique()} unique values")

print("\n=== NUMERIC SUMMARY ===")
print(df[["Sales", "Quantity", "Discount", "Profit"]].describe())

print("\n=== NEGATIVE / ZERO CHECKS ===")
print("Negative Sales:", (df["Sales"] < 0).sum())
print("Negative Profit (losses):", (df["Profit"] < 0).sum())
print("Zero Discount rows:", (df["Discount"] == 0).sum())
print("Max Discount:", df["Discount"].max())

print("\n=== ROW ID UNIQUENESS ===")
print("Row ID unique:", df["Row ID"].is_unique, "| Order ID unique:", df["Order ID"].is_unique)
