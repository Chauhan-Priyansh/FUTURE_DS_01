# FUTURE_DS_01 — Superstore Sales Analysis

**Retail Sales Analytics | Python | Pandas | Microsoft Power BI | DAX**

An end-to-end data analytics project focused on analysing retail sales, profitability, customer behaviour, product performance and regional trends using Python and Microsoft Power BI.

Developed as part of the **Future Interns Data Analytics Internship — Task 01**.

**GitHub Repository:** [FUTURE_DS_01](https://github.com/Chauhan-Priyansh/FUTURE_DS_01)

---

## 1. Project Overview

The objective of this project is to transform raw retail transaction data into meaningful business insights that support data-driven decision-making.

Using the Kaggle Sample Superstore dataset, this project implements a data analytics workflow covering:

- Data cleaning and preprocessing
- Exploratory data analysis
- Business KPI calculation
- Product and customer performance analysis
- Regional and category-level analysis
- Data modelling and DAX measures
- Interactive business intelligence dashboard development

The project combines Python-based data processing with a four-page Power BI report and a browser-based HTML dashboard preview.

## 2. Project Objectives

- Evaluate overall sales and profitability.
- Identify high-performing and loss-making products.
- Analyse category and subcategory performance.
- Understand regional and customer-level sales patterns.
- Examine monthly and yearly sales trends.
- Investigate the relationship between discounts and profitability.
- Develop actionable business recommendations.
- Present findings through an interactive Power BI dashboard.

## 3. Dataset Information

| Property | Details |
|---|---|
| Dataset | Sample Superstore |
| Source | Kaggle |
| Original records | 9,994 |
| Source columns | 21 |
| Period covered | 2014–2017 |
| Data format | CSV |

The dataset contains retail transaction information, including:

- Order and shipping details
- Customer information
- Product categories and subcategories
- Geographic information
- Sales and quantity
- Discounts and profit

**Dataset location:**

`data/kaggle/Sample - Superstore.csv`

## 4. Technology Stack

| Technology | Application |
|---|---|
| Python | Data processing and analysis |
| Pandas | Data cleaning and manipulation |
| NumPy | Numerical operations |
| Microsoft Power BI | Interactive reporting |
| DAX | Analytical measures and KPIs |
| CSV | Data storage and exchange |
| HTML / CSS / JavaScript | Browser-based dashboard |
| Git & GitHub | Version control and project hosting |

## 5. Data Processing and Methodology

The project uses a Python pipeline to prepare the original dataset and generate analytical outputs.

### Data cleaning

- Standardisation of column names and formats.
- Conversion of numerical fields into appropriate data types.
- Parsing of order and shipping dates.
- Handling of missing and invalid critical values.
- Validation of sales, profit and quantity fields.
- Preparation of cleaned transaction-level data.

### Feature engineering

Additional analytical fields are generated to support business analysis:

- Year
- Month
- Shipping duration
- Discount band
- Loss-making transaction indicator

### Data integrity and validation

During validation, a duplicate-removal issue was identified and corrected.

Two source records contained identical business attributes but had distinct Row IDs. Both represented valid source transactions and therefore needed to be preserved.

The corrected pipeline retains all **9,994 original transaction records** instead of incorrectly removing one of them.

The final analysis uses the original dataset. No simulated data was used.

## 6. Key Business KPIs

The final Python analysis produced the following validated results:

| Metric | Validated Result |
|---|---:|
| Total Sales | $2,297,200.86 |
| Total Profit | $286,397.02 |
| Profit Margin | 12.47% |
| Total Orders | 5,009 |
| Unique Customers | 793 |
| Total Quantity Sold | 37,873 |
| Records Analysed | 9,994 |

The Python-generated results and refreshed Power BI dashboard were checked for consistency.

## 7. Power BI Dashboard

The Power BI report contains four analytical pages designed to present different aspects of business performance.

### Page 1 — Sales Overview

Provides a high-level summary of overall business performance.

Includes:
- Total sales
- Total profit
- Total orders
- Customer count
- Quantity sold
- Monthly sales trends

### Page 2 — Product & Category Analysis

Examines product-level and category-level performance.

Includes:
- Category and subcategory sales
- Product profitability
- Top-performing products
- Product-level comparisons

### Page 3 — Regional & Customer Analysis

Explores geographic performance and customer behaviour.

Includes:
- Regional sales distribution
- State-level performance
- Customer segmentation
- Top customers
- Regional profitability patterns

### Page 4 — Profitability & Insights

Focuses on profitability concerns and potential business improvements.

Includes:
- Loss-making products
- Discount and profitability patterns
- Category-level profit performance
- Business findings
- Recommendations

## 8. Business Findings

The analysis highlights several areas that deserve management attention.

### Key findings

1. The business generated approximately **$2.30 million in sales** and **$286.40 thousand in profit**.
2. The overall profit margin is approximately **12.47%**.
3. Profitability varies across products, categories and subcategories.
4. Tables, Bookcases and Supplies show negative profitability in the analysis. Tables represent the largest loss at approximately **$17.7K**.
5. Discounts above 20% are associated with negative profitability in the analysed data, with an approximately **-37% margin**.
6. Machines generate approximately **$190K in sales** but only around **$3K in profit**, indicating an opportunity to review pricing and costs.

### Business recommendations

**1. Review discount policies**

Evaluate high-discount transactions and introduce more controlled discount strategies to protect profit margins.

**2. Address loss-making products**

Investigate pricing, procurement and operating costs for consistently unprofitable products.

**3. Improve product profitability**

Review pricing and cost structures for high-revenue, low-profit products such as Machines.

**4. Strengthen regional strategies**

Use geographic performance to identify opportunities for targeted sales and improved regional planning.

**5. Monitor customer performance**

Identify valuable customer segments and develop strategies to improve retention and customer value.

## 9. Project Structure

The repository is organised as follows:

```text
FUTURE_DS_01/
│
├── dashboard/
│   ├── index.html
│   └── template.html
│
├── data/
│   └── kaggle/
│       ├── FUTURE_DS_01.pbix
│       └── Sample - Superstore.csv
│
├── docs/
│   └── POWERBI_GUIDE.md
│
├── outputs/
│   ├── cleaned_superstore.csv
│   ├── cleaning_report.json
│   ├── customers.csv
│   ├── insights.md
│   ├── kpi_by_category.csv
│   ├── kpi_by_discountband.csv
│   ├── kpi_by_month.csv
│   ├── kpi_by_product.csv
│   ├── kpi_by_region.csv
│   ├── kpi_by_segment.csv
│   ├── kpi_by_shipmode.csv
│   ├── kpi_by_state.csv
│   ├── kpi_by_subcategory.csv
│   ├── kpi_by_year.csv
│   ├── loss_making_products.csv
│   ├── top_customers.csv
│   └── top_profit_products.csv
│
├── powerbi/
│   ├── dim_customer.csv
│   ├── dim_date.csv
│   ├── dim_geo.csv
│   ├── dim_product.csv
│   ├── dim_shipmode.csv
│   ├── fact_sales.csv
│   ├── FUTURE_DS_01_Dashboard.pdf
│   └── measures.dax
│
├── Screenshots/
│   ├── 01_Sales_Overview.png
│   ├── 02_Product_Category_Analysis.png
│   ├── 03_Regional_Customer_Analysis.png
│   └── 04_Profitability_Insights.png
│
├── venv/
├── analyze.py
├── README.md
├── requirements.txt
└── run_all.py
```

**Note:** The `venv/` directory is a local Python environment and should not be committed to GitHub. The repository should include `requirements.txt` so the environment can be recreated.

## 10. Getting Started

### Prerequisites

- Python 3.10 or later
- pip
- Microsoft Power BI Desktop (for opening the PBIX report)
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/Chauhan-Priyansh/FUTURE_DS_01.git
```

### Step 2 — Navigate to the project directory

```bash
cd FUTURE_DS_01
```

### Step 3 — Create a virtual environment

```bash
python -m venv venv
```

### Step 4 — Activate the environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 5 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 6 — Verify the dataset

Ensure the original Kaggle dataset is present at:

```text
data/kaggle/Sample - Superstore.csv
```

The analysis pipeline expects the source dataset to be available in this location.

### Step 7 — Run the analysis

```bash
python run_all.py
```

The pipeline generates cleaned data, analytical summaries, KPI files, Power BI source tables, DAX measures and the HTML dashboard.

## 11. Generated Outputs

The analysis pipeline generates several outputs.

| Output | Purpose |
|---|---|
| `cleaned_superstore.csv` | Cleaned transaction-level dataset |
| `cleaning_report.json` | Data-cleaning and validation summary |
| `insights.md` | Generated business insights |
| `kpi_by_*.csv` | Analytical KPI summaries |
| `customers.csv` | Customer-level analysis |
| `top_customers.csv` | Highest-performing customers |
| `loss_making_products.csv` | Products generating losses |
| `top_profit_products.csv` | Highest-profit products |
| `fact_sales.csv` | Power BI transaction fact table |
| `dim_*.csv` | Power BI dimension tables |
| `measures.dax` | DAX business measures |
| `dashboard/index.html` | Browser-based dashboard preview |

## 12. Project Deliverables

| Deliverable | Location |
|---|---|
| Python analysis pipeline | `run_all.py`, `analyze.py` |
| Original dataset | `data/kaggle/` |
| Power BI report | `data/kaggle/FUTURE_DS_01.pbix` |
| Exported dashboard PDF | `powerbi/FUTURE_DS_01_Dashboard.pdf` |
| Power BI source tables | `powerbi/` |
| DAX measures | `powerbi/measures.dax` |
| Analytical outputs | `outputs/` |
| HTML dashboard | `dashboard/index.html` |
| Power BI documentation | `docs/POWERBI_GUIDE.md` |
| Dashboard screenshots | `Screenshots/` |

## 13. Validation Summary

The final analysis was validated against the original Kaggle Sample Superstore dataset.

| Validation | Result |
|---|---:|
| Original records | 9,994 |
| Cleaned records | 9,994 |
| Total sales | $2,297,200.86 |
| Total profit | $286,397.02 |
| Unique orders | 5,009 |
| Unique customers | 793 |
| Total quantity | 37,873 |

The corrected Python pipeline and refreshed Power BI report show consistent primary KPI values.

## 14. Conclusion

This project demonstrates an end-to-end retail data analytics workflow, beginning with raw transaction data and progressing through data preparation, exploratory analysis, KPI generation, data modelling and interactive visualisation.

The final dashboard translates retail data into actionable insights concerning sales performance, product profitability, customer behaviour and regional trends.

It also demonstrates the importance of data integrity, analytical accuracy and effective business intelligence in supporting informed business decisions.

## 15. Acknowledgements

- **Future Interns** — Data Analytics Internship opportunity.
- **Kaggle** — Sample Superstore dataset.
- **Microsoft Power BI** — Business intelligence and visualisation platform.
- **Python open-source ecosystem** — Data processing and analytical tools.

---

**Project:** FUTURE_DS_01 — Superstore Sales Analysis  
**Programme:** Future Interns — Data Analytics Internship  
**Task:** Task 01  
**Repository:** [Chauhan-Priyansh/FUTURE_DS_01](https://github.com/Chauhan-Priyansh/FUTURE_DS_01)