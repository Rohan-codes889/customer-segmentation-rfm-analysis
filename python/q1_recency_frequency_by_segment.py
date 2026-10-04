"""Question 1: validate and visualize Recency and Frequency by RFM segment."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "rfm_segmented.csv"
OUTPUT = ROOT / "q1_recency_frequency_by_segment.png"

df = pd.read_csv(INPUT)
required = {"Customer ID", "Recency", "Frequency", "Segment"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")
if len(df) != 5878 or df[list(required)].isna().any().any():
    raise ValueError("Unexpected row count or missing values in input.")
if df["Customer ID"].nunique() != len(df):
    raise ValueError("Customer IDs must be unique.")

summary = (
    df.groupby("Segment", observed=True)
    .agg(
        Customers=("Customer ID", "size"),
        Median_Recency_Days=("Recency", "median"),
        Mean_Recency_Days=("Recency", "mean"),
        Recency_Q1=("Recency", lambda s: s.quantile(0.25)),
        Recency_Q3=("Recency", lambda s: s.quantile(0.75)),
        Median_Frequency=("Frequency", "median"),
        Mean_Frequency=("Frequency", "mean"),
        Frequency_Q1=("Frequency", lambda s: s.quantile(0.25)),
        Frequency_Q3=("Frequency", lambda s: s.quantile(0.75)),
    )
    .sort_values(["Median_Recency_Days", "Median_Frequency"], ascending=[True, False])
)

# Use medians: Frequency is strongly right-skewed, so a few very frequent buyers
# should not define a segment's typical customer.
labels = summary.index.tolist()
fig, axes = plt.subplots(1, 2, figsize=(14, 7.2), constrained_layout=True)
color = "#2A6F97"

for ax, column, title, xlabel in [
    (axes[0], "Median_Recency_Days", "Typical time since last purchase", "Median recency (days; lower is better)"),
    (axes[1], "Median_Frequency", "Typical number of invoices", "Median unique invoices (higher is better)"),
]:
    values = summary[column]
    bars = ax.barh(labels, values, color=color)
    ax.invert_yaxis()
    ax.set_title(title, loc="left", weight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    offset = max(values) * 0.015
    for bar, value in zip(bars, values):
        label = f"{value:,.1f}".rstrip("0").rstrip(".")
        ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2,
                label, va="center", fontsize=9)

fig.suptitle("RFM segments behave as expected: recent customers buy more often", x=0.01,
             ha="left", fontsize=16, weight="bold")
fig.savefig(OUTPUT, dpi=200, bbox_inches="tight")

display = summary.copy()
display["Mean_Recency_Days"] = display["Mean_Recency_Days"].round(1)
display["Mean_Frequency"] = display["Mean_Frequency"].round(1)
display.to_csv(ROOT / "q1_recency_frequency_summary.csv")
print(f"Validated {len(df):,} unique customers; no missing required values.")
print(display.to_string())
print(f"Chart written to: {OUTPUT.name}")
