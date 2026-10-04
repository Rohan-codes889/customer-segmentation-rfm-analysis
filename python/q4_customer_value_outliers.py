"""Question 4: high-value customers, concentration, and extreme-value checks."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
df = pd.read_csv(ROOT / "rfm_segmented.csv")
required = ["Customer ID", "Recency", "Frequency", "Monetary", "Segment"]
if set(required) - set(df.columns) or len(df) != 5878 or df["Customer ID"].nunique() != len(df):
    raise ValueError("Unexpected RFM segmentation schema or customer count.")
if df[required].isna().any().any() or (df[["Frequency", "Monetary"]] <= 0).any().any():
    raise ValueError("Required RFM values must be positive and non-missing.")

total_revenue = df["Monetary"].sum()
if abs(total_revenue - 17_374_804.27) > 0.01:
    raise ValueError(f"Monetary total failed reconciliation: £{total_revenue:,.2f}")

top_10 = df.nlargest(10, "Monetary")[required].copy()
top_10.to_csv(ROOT / "q4_top_10_customers_by_monetary.csv", index=False)

def concentration(n):
    value = df.nlargest(n, "Monetary")["Monetary"].sum()
    return n, value, 100 * value / total_revenue

top_1_n = -(-len(df) // 100)
top_5_n = -(-len(df) * 5 // 100)
concentration_table = pd.DataFrame(
    [("Top 10 customers", *concentration(10)),
     ("Top 1% of customers", *concentration(top_1_n)),
     ("Top 5% of customers", *concentration(top_5_n))],
    columns=["Group", "Customer_Count", "Revenue", "Revenue_Share_Pct"],
)
concentration_table.to_csv(ROOT / "q4_revenue_concentration_summary.csv", index=False)

def iqr_outliers(column):
    q1, q3 = df[column].quantile([0.25, 0.75])
    iqr = q3 - q1
    threshold = q3 + 1.5 * iqr
    return q1, q3, iqr, threshold, df.loc[df[column] > threshold].copy()

mon_q1, mon_q3, mon_iqr, mon_threshold, monetary_outliers = iqr_outliers("Monetary")
freq_q1, freq_q3, freq_iqr, freq_threshold, frequency_outliers = iqr_outliers("Frequency")
monetary_outliers[required].sort_values("Monetary", ascending=False).to_csv(ROOT / "q4_monetary_iqr_outliers.csv", index=False)
frequency_outliers[required].sort_values("Frequency", ascending=False).to_csv(ROOT / "q4_frequency_iqr_outliers.csv", index=False)

top_monetary = df.nlargest(1, "Monetary")[required].iloc[0]
top_frequency = df.nlargest(1, "Frequency")[required].iloc[0]

# Lorenz-style curve: customers enter from lowest to highest spending.
lorenz = df.sort_values("Monetary")["Monetary"].reset_index(drop=True).cumsum() / total_revenue
population_share = pd.Series(range(1, len(df) + 1), dtype=float) / len(df)
fig, ax = plt.subplots(figsize=(8.8, 6.6), constrained_layout=True)
ax.plot([0, 1], [0, 1], color="#9A9A9A", linestyle="--", linewidth=1.4, label="Equal revenue distribution")
ax.plot(pd.concat([pd.Series([0.0]), population_share]), pd.concat([pd.Series([0.0]), lorenz]), color="#2A6F97", linewidth=2.8, label="Observed customer revenue")
for fraction, label, offset in [(0.95, "Top 5%", (-150, 18)), (0.99, "Top 1%", (-30, 18))]:
    index = int((len(df) * fraction) - 1)
    revenue_at_bottom = lorenz.iloc[index]
    top_share = 1 - revenue_at_bottom
    ax.scatter(fraction, revenue_at_bottom, color="#C73E1D", zorder=3)
    ax.annotate(f"{label} = {top_share:.1%} of revenue", (fraction, revenue_at_bottom), xytext=offset, textcoords="offset points", fontsize=9, color="#8B2B15", arrowprops={"arrowstyle": "-", "color": "#8B2B15"})
ax.set_title("Revenue is concentrated among a small share of customers", loc="left", fontsize=15, weight="bold", pad=12)
ax.set_xlabel("Cumulative share of customers, from lowest to highest spend")
ax.set_ylabel("Cumulative share of revenue")
ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
ax.grid(alpha=0.22)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="upper left")
fig.savefig(ROOT / "q4_customer_revenue_concentration.png", dpi=200, bbox_inches="tight")

print(f"Validated {len(df):,} unique customers; Monetary total = £{total_revenue:,.2f}.")
print("\nTop 10 customers by Monetary:")
print(top_10.assign(Monetary=top_10["Monetary"].map(lambda x: f"£{x:,.2f}")).to_string(index=False))
print("\nTop-spender segment distribution:")
print(top_10["Segment"].value_counts().to_string())
print("\nRevenue concentration:")
print(concentration_table.assign(Revenue=concentration_table["Revenue"].map(lambda x: f"£{x:,.2f}"), Revenue_Share_Pct=concentration_table["Revenue_Share_Pct"].map(lambda x: f"{x:.2f}%")).to_string(index=False))
print(f"\nMonetary IQR: Q1=£{mon_q1:,.2f}, Q3=£{mon_q3:,.2f}, IQR=£{mon_iqr:,.2f}, upper threshold=£{mon_threshold:,.2f}; outliers={len(monetary_outliers):,}.")
print("Highest Monetary customer:")
print(top_monetary.to_string())
print(f"\nFrequency IQR: Q1={freq_q1:.0f}, Q3={freq_q3:.0f}, IQR={freq_iqr:.0f}, upper threshold={freq_threshold:.1f}; outliers={len(frequency_outliers):,}.")
print("Highest Frequency customer:")
print(top_frequency.to_string())
print(f"\nSame customer at both maxima: {top_monetary['Customer ID'] == top_frequency['Customer ID']}")
print("Chart written: q4_customer_revenue_concentration.png")
