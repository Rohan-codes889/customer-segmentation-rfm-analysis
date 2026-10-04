# Phase 3 SQL Setup: RFM Customer Analytics

This setup uses two tables because the files operate at two different levels. `rfm_customers` has one row per customer and stores the calculated RFM measures, scores, and segment; `retail_transactions` keeps the detailed invoice lines needed for future purchase, country, and time-based SQL analysis.

`customer_id` is an integer primary key in `rfm_customers` and a foreign key in `retail_transactions`, which makes customer-level and transaction-level results joinable without duplicating RFM values on every transaction. The CSV presents IDs such as `12346.0`, so the load statements safely convert them to whole-number IDs; money uses `DECIMAL`, rather than a floating-point type, to avoid rounding errors in currency calculations. A generated `transaction_id` gives every loaded transaction row its own stable primary key, while indexes on `customer_id` and `invoice_date` support the customer and monthly questions planned for the SQL phase.

## Load the files

Use the SQL in [phase3_rfm_schema_and_load.sql](phase3_rfm_schema_and_load.sql) in a new, empty MySQL database. It uses `LOAD DATA LOCAL INFILE`, which is substantially faster and more practical than row-by-row inserts for 779,425 transactions; start the MySQL client with `--local-infile=1` and update the two Windows paths in the script if your project is stored elsewhere.

The import expects UTF-8 CSV files, comma delimiters, and the verified timestamp format `YYYY-MM-DD HH:MM:SS`. It loads the customer table first because transactions reference it through the foreign key.

## Verify the load

The final two queries in the SQL file should return:

| Check | Expected result |
|---|---:|
| `rfm_customers` row count | 5,878 |
| `retail_transactions` row count | 779,425 |
| Transactions without a matching customer | 0 |
| Transactions with an unparsed date | 0 |

The schema and load script have been matched to the inspected CSV headers and timestamp format. They have not been executed against a MySQL server in this workspace, so treat the verification queries above—not this document—as confirmation that the local import completed successfully.
