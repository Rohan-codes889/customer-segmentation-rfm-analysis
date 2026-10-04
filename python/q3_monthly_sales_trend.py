"""Question 3: monthly revenue, active customers, and invoice trend."""
from calendar import monthrange
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "online_retail_II_cleaned_rfm.csv"

transactions = pd.read_csv(
    INPUT, usecols=["Invoice", "InvoiceDate", "Customer ID", "Quantity", "Price"]
)
required = ["Invoice", "InvoiceDate", "Customer ID", "Quantity", "Price"]
if transactions[required].isna().any().any():
    raise ValueError("Required transaction fields contain missing values.")
transactions["InvoiceDate"] = pd.to_datetime(transactions["InvoiceDate"], format="mixed", dayfirst=False)
if transactions["InvoiceDate"].isna().any():
    raise ValueError("InvoiceDate parsing failed.")
transactions["Revenue"] = transactions["Quantity"] * transactions["Price"]
transactions["Year_Month"] = transactions["InvoiceDate"].dt.to_period("M")

monthly = (
    transactions.groupby("Year_Month", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Active_Customers=("Customer ID", "nunique"),
        Unique_Invoices=("Invoice", "nunique"),
    )
)
monthly["Month_Start"] = monthly["Year_Month"].dt.to_timestamp()
monthly["Revenue_Per_Active_Customer"] = monthly["Revenue"] / monthly["Active_Customers"]
monthly["Revenue_Per_Invoice"] = monthly["Revenue"] / monthly["Unique_Invoices"]

date_min = transactions["InvoiceDate"].min()
date_max = transactions["InvoiceDate"].max()
first_period, last_period = monthly["Year_Month"].iloc[0], monthly["Year_Month"].iloc[-1]

def coverage(period):
    month_dates = transactions.loc[transactions["Year_Month"].eq(period), "InvoiceDate"]
    observed_start = month_dates.min().date()
    observed_end = month_dates.max().date()
    first_day = period.start_time.date()
    last_day = period.end_time.date()
    return {
        "month": str(period),
        "observed_start": observed_start.isoformat(),
        "observed_end": observed_end.isoformat(),
        "calendar_start": first_day.isoformat(),
        "calendar_end": last_day.isoformat(),
        "is_partial": observed_start != first_day or observed_end != last_day,
    }

first_coverage = coverage(first_period)
last_coverage = coverage(last_period)
partial_periods = [
    period for period, audit in [(first_period, first_coverage), (last_period, last_coverage)]
    if audit["is_partial"]
]

# Reconcile transaction-level monthly revenue to the already-validated project total.
total_revenue = monthly["Revenue"].sum()
if abs(total_revenue - 17_374_804.27) > 0.01:
    raise ValueError(f"Monthly revenue does not reconcile: £{total_revenue:,.2f}")
if monthly["Year_Month"].nunique() != 25:
    raise ValueError("Expected 25 monthly periods from Dec 2009 through Dec 2011.")

monthly.to_csv(ROOT / "q3_monthly_sales_summary.csv", index=False)

# The line includes all observed months; incomplete endpoints are distinct red markers
# so readers do not interpret partial month revenue as a normal comparison point.
fig, ax = plt.subplots(figsize=(13, 6.6), constrained_layout=True)
ax.plot(monthly["Month_Start"], monthly["Revenue"], color="#2A6F97", marker="o", linewidth=2.2, markersize=4)
partial = monthly[monthly["Year_Month"].isin(partial_periods)]
if not partial.empty:
    ax.scatter(partial["Month_Start"], partial["Revenue"], color="#C73E1D", s=62, zorder=3,
               label="Incomplete calendar month")
    for _, row in partial.iterrows():
        endpoint_note = "records through Dec 23" if row["Year_Month"] == first_period else "records through Dec 9"
        ax.annotate(f"{row['Year_Month']} partial\n{endpoint_note}", (row["Month_Start"], row["Revenue"]),
                    xytext=(9, 14), textcoords="offset points", fontsize=9, color="#8B2B15",
                    arrowprops={"arrowstyle": "-", "color": "#8B2B15"})

ax.set_title("Monthly revenue shows a pronounced year-end peak", loc="left", fontsize=16, weight="bold", pad=14)
ax.text(0, 1.01, "Revenue = Quantity × Price; red marker identifies an incomplete calendar month.",
        transform=ax.transAxes, color="#555555", fontsize=10)
ax.set_ylabel("Revenue (£)")
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.grid(axis="y", alpha=0.24)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
if not partial.empty:
    ax.legend(frameon=False, loc="upper left")
fig.savefig(ROOT / "q3_monthly_revenue_trend.png", dpi=200, bbox_inches="tight")

full_months = monthly.loc[~monthly["Year_Month"].isin(partial_periods)].copy()
yearly_peak = full_months.loc[full_months.groupby(full_months["Year_Month"].dt.year)["Revenue"].idxmax()]

print(f"Parsed {len(transactions):,} transactions from {date_min:%Y-%m-%d %H:%M} through {date_max:%Y-%m-%d %H:%M}.")
print(f"First-month coverage: {first_coverage}")
print(f"Last-month coverage: {last_coverage}")
print(f"Reconciliation: {len(monthly)} months; £{total_revenue:,.2f} total revenue.")
print("\nMonthly summary:")
print(monthly.assign(
    Revenue=monthly["Revenue"].map(lambda x: f"£{x:,.2f}"),
    Revenue_Per_Active_Customer=monthly["Revenue_Per_Active_Customer"].map(lambda x: f"£{x:,.2f}"),
    Revenue_Per_Invoice=monthly["Revenue_Per_Invoice"].map(lambda x: f"£{x:,.2f}"),
).to_string(index=False))
print("\nPeak complete month by year:")
print(yearly_peak[["Year_Month", "Revenue", "Active_Customers", "Unique_Invoices"]].to_string(index=False))
print("\nChart written: q3_monthly_revenue_trend.png")
