"""Why are some sub-categories so heavily discounted? Test proxies for 'slow
mover' (order frequency, discount-over-time trend) and fulfillment speed,
since this dataset has no inventory/stock-age field."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
RED, MUTED, GRID, SURFACE, INK = "#e34948", "#898781", "#e1e0d9", "#fcfcfb", "#0b0b0b"
CATEGORY_COLORS = {"Furniture": BLUE, "Office Supplies": ORANGE, "Technology": AQUA}
SEQ_BLUE_5 = ["#86b6ef", "#6da7ec", "#5598e7", "#2a78d6", "#1c5cab"]  # ordinal ramp

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": GRID,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 11,
})

df = pd.read_csv("data/raw/Sample - Superstore.csv", encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
df["Ship Lag"] = (df["Ship Date"] - df["Order Date"]).dt.days
df["Discount Band"] = pd.cut(
    df["Discount"], bins=[-0.01, 0, 0.2, 0.4, 0.6, 1.0],
    labels=["0%", "1-20%", "21-40%", "41-60%", "61-80%"]
)

OUT = "outputs/charts"
WORST = ["Tables", "Bookcases", "Supplies"]
BEST = ["Copiers", "Phones", "Accessories"]


def pct(ax, axis="x"):
    fmt = mticker.FuncFormatter(lambda x, _: f"{x:.0%}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


# 1. Demand (order-line count) vs avg discount, per sub-category -- the core hypothesis test
agg = df.groupby("Sub-Category").agg(
    orders=("Row ID", "count"), avg_discount=("Discount", "mean"), total_profit=("Profit", "sum")
)
colors = [RED if p < 0 else BLUE for p in agg["total_profit"]]
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(agg["orders"], agg["avg_discount"], s=90, color=colors, edgecolor=SURFACE, linewidth=1)
for name, row in agg.iterrows():
    ax.annotate(name, (row["orders"], row["avg_discount"]), fontsize=8.5,
                xytext=(5, 4), textcoords="offset points", color=INK)
ax.set_xlabel("Number of orders (demand/velocity proxy)")
ax.set_ylabel("Average discount")
ax.set_title("Demand vs. Discount by Sub-Category (red = net loss)")
pct(ax, axis="y")
fig.tight_layout()
fig.savefig(f"{OUT}/09_demand_vs_discount.png", dpi=150)
plt.close(fig)

# 2. Juxtaposed: quarterly order volume AND quarterly avg discount, worst-3 vs best-3
q = df.copy()
q["Quarter"] = q["Order Date"].dt.to_period("Q").dt.to_timestamp()
worst_q = q[q["Sub-Category"].isin(WORST)].groupby("Quarter").agg(
    orders=("Row ID", "count"), disc=("Discount", "mean"))
best_q = q[q["Sub-Category"].isin(BEST)].groupby("Quarter").agg(
    orders=("Row ID", "count"), disc=("Discount", "mean"))

fig, axes = plt.subplots(2, 1, figsize=(9, 7.5), sharex=True)
axes[0].plot(worst_q.index, worst_q["orders"], color=RED, linewidth=2, marker="o", markersize=4,
             label="Tables/Bookcases/Supplies (loss-makers)")
axes[0].plot(best_q.index, best_q["orders"], color=BLUE, linewidth=2, marker="o", markersize=4,
             label="Copiers/Phones/Accessories (profit drivers)")
axes[0].set_title("Quarterly Order Volume: loss-makers vs. profit drivers")
axes[0].legend(frameon=False, fontsize=9)

axes[1].plot(worst_q.index, worst_q["disc"], color=RED, linewidth=2, marker="o", markersize=4)
axes[1].plot(best_q.index, best_q["disc"], color=BLUE, linewidth=2, marker="o", markersize=4)
axes[1].set_title("Quarterly Average Discount: loss-makers vs. profit drivers")
pct(axes[1], axis="y")
fig.tight_layout()
fig.savefig(f"{OUT}/10_quarterly_volume_vs_discount.png", dpi=150)
plt.close(fig)

# 3. Juxtaposed boxplots: fulfillment lag by Category, and by Discount Band
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
cats = list(CATEGORY_COLORS.keys())
data_by_cat = [df[df["Category"] == c]["Ship Lag"] for c in cats]
bp = axes[0].boxplot(data_by_cat, tick_labels=cats, patch_artist=True, widths=0.6,
                      medianprops={"color": INK})
for patch, c in zip(bp["boxes"], cats):
    patch.set_facecolor(CATEGORY_COLORS[c])
    patch.set_alpha(0.75)
axes[0].set_title("Fulfillment Lag (days) by Category")
axes[0].set_ylabel("Days from order to ship")

bands = df["Discount Band"].cat.categories
data_by_band = [df[df["Discount Band"] == b]["Ship Lag"] for b in bands]
bp2 = axes[1].boxplot(data_by_band, tick_labels=bands, patch_artist=True, widths=0.6,
                       medianprops={"color": INK})
for patch, c in zip(bp2["boxes"], SEQ_BLUE_5):
    patch.set_facecolor(c)
axes[1].set_title("Fulfillment Lag (days) by Discount Band")
fig.tight_layout()
fig.savefig(f"{OUT}/11_shiplag_category_vs_discountband.png", dpi=150)
plt.close(fig)

# 4. Juxtaposed: avg discount by Ship Mode, and order count by Ship Mode
by_mode = df.groupby("Ship Mode").agg(avg_discount=("Discount", "mean"), orders=("Row ID", "count"))
by_mode = by_mode.sort_values("orders", ascending=False)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
axes[0].bar(by_mode.index, by_mode["avg_discount"], color=[BLUE, ORANGE, AQUA, YELLOW])
axes[0].set_title("Average Discount by Ship Mode")
pct(axes[0], axis="y")
axes[1].bar(by_mode.index, by_mode["orders"], color=[BLUE, ORANGE, AQUA, YELLOW])
axes[1].set_title("Order Volume by Ship Mode")
fig.tight_layout()
fig.savefig(f"{OUT}/12_shipmode_discount_vs_volume.png", dpi=150)
plt.close(fig)

# 5. Quantity vs Discount, by Category -- is discount a bulk-order lever?
fig, ax = plt.subplots(figsize=(8, 5))
for cat, color in CATEGORY_COLORS.items():
    sub = df[df["Category"] == cat]
    ax.scatter(sub["Quantity"], sub["Discount"], s=16, alpha=0.4, color=color, label=cat)
ax.set_xlabel("Quantity ordered")
ax.set_ylabel("Discount")
ax.set_title("Order Quantity vs. Discount, by Category")
ax.legend(frameon=False)
pct(ax, axis="y")
fig.tight_layout()
fig.savefig(f"{OUT}/13_quantity_vs_discount.png", dpi=150)
plt.close(fig)

# 6. Discount distribution by Segment
fig, ax = plt.subplots(figsize=(7, 5))
segs = df["Segment"].unique().tolist()
data_by_seg = [df[df["Segment"] == s]["Discount"] for s in segs]
bp3 = ax.boxplot(data_by_seg, tick_labels=segs, patch_artist=True, widths=0.6, medianprops={"color": INK})
for patch, c in zip(bp3["boxes"], [BLUE, ORANGE, AQUA]):
    patch.set_facecolor(c)
    patch.set_alpha(0.75)
ax.set_title("Discount Distribution by Customer Segment")
pct(ax, axis="y")
fig.tight_layout()
fig.savefig(f"{OUT}/14_discount_by_segment.png", dpi=150)
plt.close(fig)

print("Saved 6 investigation charts to outputs/charts/")

print("\n=== SUMMARY NUMBERS ===")
print(agg.sort_values("avg_discount", ascending=False))
print("\nShip Lag overall: mean", df["Ship Lag"].mean().round(2), "median", df["Ship Lag"].median())
print("\nShip Lag by discount band:\n", df.groupby("Discount Band")["Ship Lag"].mean())
print("\nCorrelation Discount vs Ship Lag:", df["Discount"].corr(df["Ship Lag"]).round(3))
print("Correlation Quantity vs Discount:", df["Quantity"].corr(df["Discount"]).round(3))
