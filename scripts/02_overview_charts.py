"""First-look exploratory charts: understand the shape of the business before
asking specific questions. Saves PNGs to outputs/charts/."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# --- palette (validated categorical + diverging pair) ---
BLUE = "#2a78d6"     # categorical slot 1 -- used for "Sales"
ORANGE = "#eb6834"   # categorical slot 2 -- used for "Profit"
AQUA = "#1baf7a"     # categorical slot 3
RED = "#e34948"      # diverging pole -- loss
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})

df = pd.read_csv("data/raw/Sample - Superstore.csv", encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")

OUT = "outputs/charts"


def currency(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


# 1. Monthly Sales trend
monthly = df.set_index("Order Date").resample("ME")[["Sales", "Profit"]].sum()
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(monthly.index, monthly["Sales"], color=BLUE, linewidth=2)
ax.set_title("Monthly Sales, 2014–2017")
currency(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/01_monthly_sales.png", dpi=150)
plt.close(fig)

# 2. Monthly Profit trend (zero reference line, no dual axis)
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(monthly.index, monthly["Profit"], color=ORANGE, linewidth=2)
ax.axhline(0, color=MUTED, linewidth=1)
ax.set_title("Monthly Profit, 2014–2017")
currency(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/02_monthly_profit.png", dpi=150)
plt.close(fig)

# 3. Sales & Profit by Category (grouped bar)
by_cat = df.groupby("Category")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
fig, ax = plt.subplots(figsize=(7, 4.5))
x = range(len(by_cat))
w = 0.35
ax.bar([i - w / 2 for i in x], by_cat["Sales"], width=w, color=BLUE, label="Sales")
ax.bar([i + w / 2 for i in x], by_cat["Profit"], width=w, color=ORANGE, label="Profit")
ax.set_xticks(list(x))
ax.set_xticklabels(by_cat.index)
ax.axhline(0, color=MUTED, linewidth=1)
ax.set_title("Sales vs. Profit by Category")
ax.legend(frameon=False)
currency(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/03_category_sales_profit.png", dpi=150)
plt.close(fig)

# 4. Profit by Sub-Category, sorted, diverging color by sign (the loss-makers view)
by_subcat = df.groupby("Sub-Category")["Profit"].sum().sort_values()
colors = [RED if v < 0 else BLUE for v in by_subcat.values]
fig, ax = plt.subplots(figsize=(7, 7))
ax.barh(by_subcat.index, by_subcat.values, color=colors)
ax.axvline(0, color=MUTED, linewidth=1)
ax.set_title("Total Profit by Sub-Category (red = loss-making)")
currency(ax, axis="x")
fig.tight_layout()
fig.savefig(f"{OUT}/04_subcategory_profit.png", dpi=150)
plt.close(fig)

# 5. Sales & Profit by Region (grouped bar)
by_region = df.groupby("Region")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
fig, ax = plt.subplots(figsize=(7, 4.5))
x = range(len(by_region))
ax.bar([i - w / 2 for i in x], by_region["Sales"], width=w, color=BLUE, label="Sales")
ax.bar([i + w / 2 for i in x], by_region["Profit"], width=w, color=ORANGE, label="Profit")
ax.set_xticks(list(x))
ax.set_xticklabels(by_region.index)
ax.set_title("Sales vs. Profit by Region")
ax.legend(frameon=False)
currency(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/05_region_sales_profit.png", dpi=150)
plt.close(fig)

# 6. Sales by Segment
by_segment = df.groupby("Segment")["Sales"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.bar(by_segment.index, by_segment.values, color=BLUE)
ax.set_title("Total Sales by Customer Segment")
currency(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/06_segment_sales.png", dpi=150)
plt.close(fig)

# 7. Discount vs Profit scatter, colored by Category
cat_colors = {"Furniture": BLUE, "Office Supplies": ORANGE, "Technology": AQUA}
fig, ax = plt.subplots(figsize=(8, 5))
for cat, color in cat_colors.items():
    sub = df[df["Category"] == cat]
    ax.scatter(sub["Discount"], sub["Profit"], s=14, alpha=0.5, color=color, label=cat)
ax.axhline(0, color=MUTED, linewidth=1)
ax.set_xlabel("Discount")
ax.set_ylabel("Profit")
ax.set_title("Discount vs. Profit, by Category")
ax.legend(frameon=False)
currency(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/07_discount_vs_profit.png", dpi=150)
plt.close(fig)

# 8. Profit distribution histogram
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(df["Profit"], bins=60, color=BLUE, edgecolor=SURFACE)
ax.axvline(0, color=RED, linewidth=1.5)
ax.set_title("Distribution of Profit per Line Item")
currency(ax, axis="x")
fig.tight_layout()
fig.savefig(f"{OUT}/08_profit_distribution.png", dpi=150)
plt.close(fig)

print("Saved 8 charts to outputs/charts/")
