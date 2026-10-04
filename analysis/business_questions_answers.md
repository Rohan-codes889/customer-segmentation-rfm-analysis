# Customer Segmentation: Business Questions Answered

## 1. Who are the most valuable customers?

Champions are the most valuable segment: 1,257 customers (21.4% of the base) generate £11.74m, or 67.5% of total revenue, and their typical customer purchased 16 days ago and has 11 invoices. At the individual level, customer 18102 is the largest spender at £580,987.04 (145 invoices, 1 day since purchase), followed by customer 14646 at £528,602.52; both are Champions. The top 10 customers generate 16.04% of all revenue, so these accounts warrant individual attention alongside the broader Champion segment.

## 2. Which customers are at risk of becoming inactive?

Can't Lose Them are the clearest immediate win-back group: their typical customer has 7 invoices but has not purchased for 326.5 days, and the segment still represents £933,144.75 in historical revenue. At Risk customers are even less recent (median 378 days) with 4 invoices and £632,234.40 in revenue; Hibernating and Lost customers have still longer inactivity and lower typical frequency. These groups should not receive the same treatment: protect high-value, formerly frequent customers first, then use lower-cost reactivation for lower-value inactive groups.

## 3. Which customers show potential to become loyal?

Potential Loyalists are the main upgrade opportunity: 707 customers have a median recency of 23 days and 3 invoices, indicating recent engagement but not yet Champion-level repeat buying. Recent Customers are also newly engaged (29-day median recency) but usually have only one invoice, while Promising customers are less recent at 96 days and also typically have one invoice. A timely second-purchase or cross-sell journey is most relevant for these groups, especially Potential Loyalists, before their recency worsens.

## 4. Which customer segments generate the most revenue?

Champions dominate with £11.74m (67.54% of revenue), followed by Loyal Customers at £1.84m (10.58%) and Can't Lose Them at £0.93m (5.37%). Potential Loyalists contribute £0.86m (4.98%), while At Risk and Need Attention each contribute about £0.63m (3.64% and 3.67%). Revenue is therefore concentrated both in active high-value customers and in a smaller set of valuable customers whose engagement has deteriorated.

## 5. Where should retention efforts be focused?

First, protect UK-based Champions and the highest-value individual accounts: the UK produces 82.82% of revenue, Champions produce 67.54%, and the top 5% of customers generate 52.00% of total revenue. Second, run a targeted win-back programme for Can't Lose Them, then At Risk, because their historical purchase frequency and revenue make recovery more valuable than broad outreach to all inactive customers. Customer 16446 should be manually reviewed before treatment because £168,472.50 comes from only two invoices; this could be a bulk-order account or an underlying transaction issue.

## 6. Which countries contribute significantly to revenue?

The United Kingdom is the core market, contributing £14.39m (82.82% of revenue) and 5,350 customers (91.02% of the customer base). The largest non-UK revenue contributors are EIRE (£616,368.98), the Netherlands (£554,038.09), Germany (£424,922.66), and France (£349,107.36). EIRE and the Netherlands achieve their revenue from very few customers (4 and 22 respectively), so their figures may be influenced by wholesale-like accounts and should not be treated as straightforward broad-market expansion evidence.

## 7. What patterns exist between recency, frequency, and monetary value?

The RFM patterns behave logically: Champions combine low recency (16 days) with high frequency (11 invoices) and account for most revenue, while Lost customers have a 576.5-day median recency and typically one invoice. Loyal Customers remain relatively frequent (7 invoices) but are less recent (78 days), whereas Can't Lose Them retain the same typical frequency but have a much longer 326.5-day gap since purchase. The relationship is not perfect at the individual level: customer 16446 has only two invoices but £168,472.50 in value, showing why frequency alone cannot identify every high-value account.

---

All figures are based on the verified Phase 1 EDA outputs from `rfm_segmented.csv`, the customer/country summaries, and the monthly sales analysis. Revenue is measured as `Quantity × Price` after the project cleaning rules were applied.
