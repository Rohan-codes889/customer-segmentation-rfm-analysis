# Data

This project uses the **Online Retail II** dataset from the UCI Machine Learning Repository.

## Dataset

The dataset contains transactional records from an online retail store, including:

- Invoice information
- Product descriptions
- Quantity
- Price
- Customer ID
- Country
- Transaction date

## Data Processing

The original dataset was cleaned and transformed for customer-level RFM analysis.

The workflow was:

Raw Transaction Data  
→ Data Cleaning  
→ RFM Customer Table  
→ Customer Segmentation  
→ SQL Analysis  
→ Power BI Dashboard

The final segmented dataset contains **5,878 customers**.

## Included File

- `rfm_segmented.csv` — final customer-level dataset containing RFM metrics, scores, and customer segments.

## Dataset Availability

The original raw dataset and large intermediate transaction files are not included in this repository due to their size.

The dataset was used for educational and portfolio analysis purposes.
