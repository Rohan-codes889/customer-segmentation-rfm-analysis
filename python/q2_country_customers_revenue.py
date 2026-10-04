"""Question 2: audit country mapping and summarize customers and revenue."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
RFM_PATH = ROOT / "rfm_segmented.csv"
TXN_PATH = ROOT / "online_retail_II_cleaned_rfm.csv"

rfm = pd.read_csv(RFM_PATH)
transactions = pd.read_csv(TXN_PATH, usecols=["Customer ID", "Country", "Quantity", "Price"])

required_rfm = {"Customer ID", "Monetary", "Segment"}
if required_rfm - set(rfm.columns):
    raise ValueError("The RFM file does not have its expected columns.")
if len(rfm) != 5878 or rfm["Customer ID"].nunique() != len(rfm):
    raise ValueError("Expected exactly 5,878 unique customers in the RFM file.")
if rfm[["Customer ID", "Monetary"]].isna().any().any():
    raise ValueError("RFM customer IDs and Monetary values must be present.")
if transactions[["Customer ID", "Country", "Quantity", "Price"]].isna().any().any():
    raise ValueError("Cleaned transaction customer IDs and countries must be present.")

# A distinct-country audit must happen before reducing transactions to one country/customer.
country_audit = (
    transactions.groupby("Customer ID", as_index=False)["Country"]
    .nunique()
    .rename(columns={"Country": "Distinct_Countries"})
)
multi_country = country_audit.query("Distinct_Countries > 1")
customer_country_pairs = transactions.drop_duplicates(["Customer ID", "Country"])

if not multi_country.empty:
    details = (
        customer_country_pairs[customer_country_pairs["Customer ID"].isin(multi_country["Customer ID"])]
        .sort_values("Customer ID")
    )
    details.to_csv(ROOT / "q2_customers_with_multiple_countries.csv", index=False)

    # The agreed resolution is based on transaction revenue, not transaction count.
    transaction_country_revenue = (
        transactions.assign(Transaction_Revenue=transactions["Quantity"] * transactions["Price"])
        .groupby(["Customer ID", "Country"], as_index=False)["Transaction_Revenue"].sum()
    )
    multi_revenue = transaction_country_revenue[
        transaction_country_revenue["Customer ID"].isin(multi_country["Customer ID"])
    ].copy()
    max_revenue = multi_revenue.groupby("Customer ID")["Transaction_Revenue"].transform("max")
    assigned_multi = multi_revenue.loc[multi_revenue["Transaction_Revenue"].eq(max_revenue)].copy()
    if assigned_multi["Customer ID"].duplicated().any():
        raise ValueError("A multi-country customer has tied highest country revenue; an additional tie-break rule is required.")
    assigned_multi = assigned_multi.rename(columns={"Country": "Assigned_Country"})[
        ["Customer ID", "Assigned_Country"]
    ]
    revenue_text = (
        multi_revenue.sort_values(["Customer ID", "Country"])
        .assign(Country_Revenue=lambda x: x.apply(
            lambda row: f"{row['Country']} (£{row['Transaction_Revenue']:,.2f})", axis=1
        ))
        .groupby("Customer ID", as_index=False)["Country_Revenue"].agg("; ".join)
        .rename(columns={"Country_Revenue": "Revenue_by_Country"})
    )
    multi_audit = (
        revenue_text.merge(assigned_multi, on="Customer ID", validate="one_to_one")
        .sort_values("Customer ID")
    )
    multi_audit.to_csv(ROOT / "q2_multi_country_revenue_assignment_audit.csv", index=False)
    customer_country = pd.concat(
        [
            customer_country_pairs.loc[
                ~customer_country_pairs["Customer ID"].isin(multi_country["Customer ID"]),
                ["Customer ID", "Country"],
            ],
            assigned_multi.rename(columns={"Assigned_Country": "Country"}),
        ],
        ignore_index=True,
    )
else:
    multi_audit = pd.DataFrame(columns=["Customer ID", "Revenue_by_Country", "Assigned_Country"])
    customer_country = customer_country_pairs[["Customer ID", "Country"]].copy()

if customer_country["Customer ID"].duplicated().any():
    raise ValueError("Final customer-to-country mapping must have one country per customer.")
joined = rfm[["Customer ID", "Monetary"]].merge(
    customer_country, on="Customer ID", how="left", validate="one_to_one"
)
if joined["Country"].isna().any():
    raise ValueError(f"{joined['Country'].isna().sum()} RFM customers did not map to a country.")

summary = (
    joined.groupby("Country", as_index=False)
    .agg(Customers=("Customer ID", "size"), Revenue=("Monetary", "sum"))
)
total_customers = summary["Customers"].sum()
total_revenue = summary["Revenue"].sum()
summary["Customer_Share_Pct"] = 100 * summary["Customers"] / total_customers
summary["Revenue_Share_Pct"] = 100 * summary["Revenue"] / total_revenue
summary = summary.sort_values("Revenue", ascending=False)

if total_customers != len(rfm) or abs(total_revenue - rfm["Monetary"].sum()) > 0.01:
    raise ValueError("Country totals do not reconcile to RFM totals.")

top_revenue = summary.head(10).copy()
top_customers = summary.sort_values("Customers", ascending=False).head(10).copy()
top_revenue.to_csv(ROOT / "q2_top_10_countries_by_revenue.csv", index=False)
top_customers.to_csv(ROOT / "q2_top_10_countries_by_customers.csv", index=False)
summary.to_csv(ROOT / "q2_country_summary_all.csv", index=False)

def format_table(frame):
    view = frame.copy()
    view["Revenue"] = view["Revenue"].map(lambda x: f"£{x:,.2f}")
    for column in ["Customer_Share_Pct", "Revenue_Share_Pct"]:
        view[column] = view[column].map(lambda x: f"{x:.2f}%")
    return view.to_string(index=False)

def plot_revenue(frame, output, title, subtitle):
    data = frame.sort_values("Revenue")
    fig, ax = plt.subplots(figsize=(10, 6.5), constrained_layout=True)
    bars = ax.barh(data["Country"], data["Revenue"], color="#2A6F97")
    ax.set_title(title, loc="left", fontsize=15, weight="bold", pad=12)
    ax.text(0, 1.01, subtitle, transform=ax.transAxes, color="#555555", fontsize=10)
    ax.set_xlabel("Customer-level revenue (£)")
    ax.grid(axis="x", alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    offset = data["Revenue"].max() * 0.012
    for bar, value in zip(bars, data["Revenue"]):
        ax.text(value + offset, bar.get_y() + bar.get_height() / 2,
                f"£{value / 1_000_000:.2f}m", va="center", fontsize=9)
    fig.savefig(ROOT / output, dpi=200, bbox_inches="tight")

plot_revenue(top_revenue, "q2_top_10_countries_by_revenue.png",
             "Revenue is concentrated in the United Kingdom",
             "Top 10 countries by revenue; values sum customer-level Monetary totals.")

uk = summary.loc[summary["Country"].eq("United Kingdom")]
uk_revenue_share = uk["Revenue_Share_Pct"].iloc[0] if not uk.empty else 0
if uk_revenue_share >= 75:
    non_uk = summary.loc[~summary["Country"].eq("United Kingdom")].head(10)
    plot_revenue(non_uk, "q2_top_10_non_uk_countries_by_revenue.png",
                 "Largest revenue markets outside the United Kingdom",
                 "Top 10 non-UK countries by revenue; makes the international opportunity visible.")

print(f"Mapping audit: {len(country_audit):,} transaction customers checked; {len(multi_country):,} map to multiple countries.")
if not multi_audit.empty:
    print("\nMulti-country assignment audit (assigned to highest transaction-revenue country):")
    print(multi_audit.to_string(index=False))
print(f"Join audit: {len(joined):,} RFM customers mapped; {joined['Country'].isna().sum():,} unmapped.")
print(f"Reconciliation: {total_customers:,} customers; £{total_revenue:,.2f} country revenue; RFM difference £{total_revenue - rfm['Monetary'].sum():.2f}.")
print("\nTop 10 by revenue:\n" + format_table(top_revenue))
print("\nTop 10 by customers:\n" + format_table(top_customers))
print(f"\nUnited Kingdom share: {uk_revenue_share:.2f}% of revenue.")
print("Charts written: q2_top_10_countries_by_revenue.png" + (", q2_top_10_non_uk_countries_by_revenue.png" if uk_revenue_share >= 75 else ""))
