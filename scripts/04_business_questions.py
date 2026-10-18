"""Answer the five locked-in business questions with charts in outputs/charts/."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
RED, MUTED, GRID, SURFACE, INK = "#e34948", "#898781", "#e1e0d9", "#fcfcfb", "#0b0b0b"
CATEGORY_COLORS = {"Furniture": BLUE, "Office Supplies": ORANGE, "Technology": AQUA}

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": GRID,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 11,
})

df = pd.read_csv("data/raw/Sample - Superstore.csv", encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
OUT = "outputs/charts"


def currency(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def pct(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"{x:.0%}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


# Q1. Profit MARGIN trend over time (not just raw profit)
monthly = df.set_index("Order Date").resample("ME")[["Sales", "Profit"]].sum()
monthly["Margin"] = monthly["Profit"] / monthly["Sales"]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(monthly.index, monthly["Margin"], color=BLUE, linewidth=2)
ax.axhline(0, color=RED, linewidth=1)
ax.axhline(monthly["Margin"].mean(), color=MUTED, linewidth=1, linestyle="--")
ax.set_title("Monthly Profit Margin (Profit / Sales), with overall average")
pct(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/15_margin_trend.png", dpi=150)
plt.close(fig)

# Q2. Discount ceiling -- profit margin by discount band, per category (small multiples)
df["Discount Band"] = pd.cut(df["Discount"], bins=[-0.01, 0, 0.2, 0.3, 0.4, 0.5, 1.0],
                              labels=["0%", "1-20%", "21-30%", "31-40%", "41-50%", "51-80%"])
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
for ax, (cat, color) in zip(axes, CATEGORY_COLORS.items()):
    sub = df[df["Category"] == cat]
    by_band = sub.groupby("Discount Band", observed=True).apply(
        lambda g: g["Profit"].sum() / g["Sales"].sum() if g["Sales"].sum() else 0, include_groups=False)
    bar_colors = [RED if v < 0 else color for v in by_band.values]
    ax.bar(by_band.index.astype(str), by_band.values, color=bar_colors)
    ax.axhline(0, color=MUTED, linewidth=1)
    ax.set_title(cat)
    ax.tick_params(axis="x", rotation=45)
    pct(ax)
fig.suptitle("Profit Margin by Discount Band, per Category (red = net loss)")
fig.tight_layout()
fig.savefig(f"{OUT}/16_discount_ceiling_by_category.png", dpi=150)
plt.close(fig)

# Q3. Fix-or-drop: sub-category profit vs profit MARGIN (not just totals)
agg = df.groupby("Sub-Category").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
agg["margin"] = agg["profit"] / agg["sales"]
agg = agg.sort_values("profit")
colors = [RED if v < 0 else BLUE for v in agg["profit"]]
fig, axes = plt.subplots(1, 2, figsize=(13, 6.5), sharey=True)
axes[0].barh(agg.index, agg["profit"], color=colors)
axes[0].axvline(0, color=MUTED, linewidth=1)
axes[0].set_title("Total Profit ($)")
currency(axes[0], axis="x")
colors2 = [RED if v < 0 else BLUE for v in agg["margin"]]
axes[1].barh(agg.index, agg["margin"], color=colors2)
axes[1].axvline(0, color=MUTED, linewidth=1)
axes[1].set_title("Profit Margin (%)")
pct(axes[1], axis="x")
fig.suptitle("Sub-Category: Total Profit vs. Profit Margin (same sort order)")
fig.tight_layout()
fig.savefig(f"{OUT}/17_subcategory_profit_vs_margin.png", dpi=150)
plt.close(fig)

# Q4. Geographic efficiency: Sales vs Margin by State (highlight high-sales / low-margin)
by_state = df.groupby("State").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
by_state["margin"] = by_state["profit"] / by_state["sales"]
colors = [RED if v < 0 else (ORANGE if v < 0.08 else BLUE) for v in by_state["margin"]]
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(by_state["sales"], by_state["margin"], s=40, color=colors, alpha=0.8, edgecolor=SURFACE)
for name, row in by_state.iterrows():
    if row["sales"] > 70000 or row["margin"] < -0.05:
        ax.annotate(name, (row["sales"], row["margin"]), fontsize=8,
                    xytext=(5, 4), textcoords="offset points", color=INK)
ax.axhline(0, color=RED, linewidth=1)
ax.set_xlabel("Total Sales")
ax.set_ylabel("Profit Margin")
ax.set_title("State: Sales vs. Profit Margin (red = net loss, orange = thin margin <8%)")
currency(ax, axis="x")
pct(ax)
fig.tight_layout()
fig.savefig(f"{OUT}/18_state_sales_vs_margin.png", dpi=150)
plt.close(fig)

# Q5. Where to double down: Category x Segment profit margin heatmap
pivot = df.groupby(["Category", "Segment"]).apply(
    lambda g: g["Profit"].sum() / g["Sales"].sum(), include_groups=False).unstack()
fig, ax = plt.subplots(figsize=(7, 4.5))
im = ax.imshow(pivot.values, cmap="RdBu", vmin=-0.1, vmax=0.25)
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        ax.text(j, i, f"{pivot.values[i, j]:.0%}", ha="center", va="center", color=INK)
ax.set_title("Profit Margin: Category x Segment")
fig.colorbar(im, ax=ax, format=mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))
fig.tight_layout()
fig.savefig(f"{OUT}/19_category_segment_margin_heatmap.png", dpi=150)
plt.close(fig)

print("Saved 5 business-question charts to outputs/charts/")
print("\nSub-category profit & margin:\n", agg)
print("\nWorst 5 states by margin:\n", by_state.sort_values("margin").head())
