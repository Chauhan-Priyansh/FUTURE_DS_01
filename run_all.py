
"""
FUTURE_DS_01 — Superstore Business Sales Performance Analytics

Processes the real Kaggle Superstore dataset and generates:
- Cleaned transaction data
- KPI and customer analysis CSV files
- Business insights and recommendations
- Power BI star-schema tables
- DAX measures
- Interactive HTML dashboard data

Run from the project root:
    python analyze.py

The script requires exactly one CSV in data/kaggle/.
It does not generate or use simulated data.
"""

from pathlib import Path
import json
import os

import numpy as np
import pandas as pd


# ============================================================
# 1. PROJECT PATHS AND DATASET VALIDATION
# ============================================================

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

DATA_DIR = ROOT / "data" / "kaggle"

OUTPUT_DIR = ROOT / "outputs"
POWERBI_DIR = ROOT / "powerbi"
DASHBOARD_DIR = ROOT / "dashboard"

for folder in [OUTPUT_DIR, POWERBI_DIR, DASHBOARD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

csv_files = sorted(DATA_DIR.glob("*.csv"))

if len(csv_files) == 0:
    raise SystemExit(
        "ERROR: No CSV dataset found in data/kaggle/.\n"
        "Place the original Kaggle Sample Superstore CSV there."
    )

if len(csv_files) > 1:
    raise SystemExit(
        "ERROR: Multiple CSV files found in data/kaggle/.\n"
        "Keep only the original Sample Superstore dataset."
    )

SOURCE_FILE = csv_files[0]
SOURCE_NAME = SOURCE_FILE.name

print("=" * 60)
print("FUTURE_DS_01 — SUPERSTORE ANALYTICS")
print("=" * 60)
print(f"Dataset: {SOURCE_NAME}")


# ============================================================
# 2. LOAD DATA
# ============================================================

try:
    raw = pd.read_csv(SOURCE_FILE)
except UnicodeDecodeError:
    raw = pd.read_csv(SOURCE_FILE, encoding="latin-1")

raw_rows = len(raw)

print(f"Original records: {raw_rows:,}")


# ============================================================
# 3. STANDARDISE COLUMN NAMES
# ============================================================

ALIASES = {
    "Order ID": ["orderid"],
    "Order Date": ["orderdate"],
    "Ship Date": ["shipdate"],
    "Ship Mode": ["shipmode"],
    "Customer ID": ["customerid"],
    "Customer Name": ["customername"],
    "Segment": ["segment"],
    "City": ["city"],
    "State": ["state", "province"],
    "Region": ["region"],
    "Product ID": ["productid"],
    "Category": ["category"],
    "Sub-Category": ["subcategory"],
    "Product Name": ["productname", "product"],
    "Sales": ["sales"],
    "Quantity": ["quantity"],
    "Discount": ["discount"],
    "Profit": ["profit"]
}


def normalise_column(name):
    """Remove spaces and common separators for column matching."""
    return (
        str(name)
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


normalised_columns = {
    column: normalise_column(column)
    for column in raw.columns
}

rename_map = {}

for standard_name, aliases in ALIASES.items():
    for alias in aliases:
        matches = [
            column
            for column, normalised in normalised_columns.items()
            if normalised == alias and column not in rename_map
        ]

        if matches:
            rename_map[matches[0]] = standard_name
            break

df = raw.rename(columns=rename_map).copy()

# Keep only recognised columns.
df = df[list(dict.fromkeys(rename_map.values()))].copy()


# ============================================================
# 4. VALIDATE REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "Order Date",
    "Sales",
    "Profit",
    "Product Name",
    "Category",
    "Region"
]

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:
    raise SystemExit(
        "ERROR: Required columns are missing:\n"
        + ", ".join(missing_columns)
    )


# ============================================================
# 5. ADD OPTIONAL COLUMNS IF NEEDED
# ============================================================

DEFAULT_COLUMNS = {
    "Order ID": "Unknown",
    "Customer ID": "Unknown",
    "Customer Name": "Unknown",
    "Segment": "Unknown",
    "City": "Unknown",
    "State": "Unknown",
    "Ship Mode": "Unknown",
    "Sub-Category": "Unknown"
}

for column, default_value in DEFAULT_COLUMNS.items():
    if column not in df.columns:
        df[column] = default_value

if "Product ID" not in df.columns:
    df["Product ID"] = df["Product Name"]

if "Quantity" not in df.columns:
    df["Quantity"] = 1

if "Discount" not in df.columns:
    df["Discount"] = 0.0

if "Ship Date" not in df.columns:
    df["Ship Date"] = pd.NaT


# ============================================================
# 6. INITIALISE CLEANING REPORT
# ============================================================

cleaning_report = {
    "source_file": SOURCE_NAME,
    "using_demo_data": False,
    "raw_rows": raw_rows
}


# ============================================================
# 7. REMOVE EXACT DUPLICATES
# ============================================================# Preserve all source transaction records.
# Repeated transaction details with distinct Row IDs are valid.
cleaning_report["duplicates_removed"] = 0

# ============================================================
# 8. DATE CONVERSION
# ============================================================

DATE_FORMATS = [
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%m-%d-%Y",
    "%d-%m-%Y",
    "%m/%d/%Y %H:%M",
    "%Y-%m-%d %H:%M:%S"
]


def parse_dates(series):
    """Parse dates using supported common date formats."""

    values = series.astype("string").str.strip()

    parsed_versions = [
        pd.to_datetime(
            values,
            format=date_format,
            errors="coerce"
        )
        for date_format in DATE_FORMATS
    ]

    # Choose the format that successfully parses the most dates.
    order = sorted(
        range(len(parsed_versions)),
        key=lambda index: -parsed_versions[index].notna().sum()
    )

    result = parsed_versions[order[0]].copy()

    # Fill remaining missing dates from other successful formats.
    for index in order[1:]:
        result = result.fillna(parsed_versions[index])

    return result


df["Order Date"] = parse_dates(df["Order Date"])
df["Ship Date"] = parse_dates(df["Ship Date"])

before = len(df)

df = df.dropna(subset=["Order Date"]).copy()

cleaning_report["bad_dates_dropped"] = before - len(df)

if df.empty:
    raise SystemExit(
        "ERROR: No valid order dates were found in the dataset."
    )


# ============================================================
# 9. NUMERIC DATA CONVERSION
# ============================================================

NUMERIC_COLUMNS = [
    "Sales",
    "Profit",
    "Quantity",
    "Discount"
]

for column in NUMERIC_COLUMNS:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

before = len(df)

df = df.dropna(
    subset=["Sales", "Profit"]
).copy()

cleaning_report["missing_sales_or_profit_dropped"] = (
    before - len(df)
)

if df.empty:
    raise SystemExit(
        "ERROR: No valid sales and profit records remain."
    )


# ============================================================
# 10. QUANTITY AND DISCOUNT CLEANING
# ============================================================

df["Quantity"] = df["Quantity"].fillna(1)

before = len(df)

df = df[df["Quantity"] > 0].copy()

cleaning_report["bad_quantity_dropped"] = before - len(df)

if df.empty:
    raise SystemExit(
        "ERROR: No valid positive-quantity records remain."
    )

df["Discount"] = (
    df["Discount"]
    .fillna(0)
    .clip(0, 1)
)


# ============================================================
# 11. TEXT STANDARDISATION
# ============================================================

TEXT_COLUMNS = [
    "Segment",
    "Region",
    "Category",
    "Sub-Category",
    "Ship Mode",
    "City",
    "State"
]

for column in TEXT_COLUMNS:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .str.title()
        .fillna("Unknown")
    )

df["Product Name"] = (
    df["Product Name"]
    .astype("string")
    .str.strip()
    .fillna("Unknown")
)

for column in [
    "Order ID",
    "Customer ID",
    "Customer Name",
    "Product ID"
]:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .fillna("Unknown")
    )


# ============================================================
# 12. CREATE ANALYTICAL COLUMNS
# ============================================================

df["Year"] = df["Order Date"].dt.year

df["Month"] = (
    df["Order Date"]
    .dt.strftime("%Y-%m")
)

df["ShipDays"] = (
    df["Ship Date"] - df["Order Date"]
).dt.days

discount_bins = [
    -0.001,
    0,
    0.1,
    0.2,
    0.3,
    0.5,
    1
]

discount_labels = [
    "No discount",
    "1-10%",
    "11-20%",
    "21-30%",
    "31-50%",
    "Over 50%"
]

df["DiscountBand"] = pd.cut(
    df["Discount"],
    bins=discount_bins,
    labels=discount_labels
).astype("string")

df["DiscountBand"] = (
    df["DiscountBand"]
    .fillna("Unknown")
)

df["Profit Status"] = np.where(
    df["Profit"] < 0,
    "Loss",
    "Profit"
)

df["IsLossLine"] = (
    df["Profit"] < 0
).astype(int)

df["Shipping Days"] = df["ShipDays"]

df["Sales per Unit"] = np.where(
    df["Quantity"] > 0,
    df["Sales"] / df["Quantity"],
    0
)

cleaning_report["clean_rows"] = len(df)

cleaning_report["customers"] = int(
    df["Customer ID"].nunique()
)

cleaning_report["orders"] = int(
    df["Order ID"].nunique()
)

cleaning_report["missing_region_labelled"] = int(
    df["Region"].eq("Unknown").sum()
)

df = df.sort_values(
    "Order Date"
).reset_index(drop=True)


# ============================================================
# 13. EXPORT CLEANED DATA
# ============================================================

df.to_csv(
    OUTPUT_DIR / "cleaned_superstore.csv",
    index=False
)

with open(
    OUTPUT_DIR / "cleaning_report.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        cleaning_report,
        file,
        indent=2
    )


# ============================================================
# 14. KPI GENERATION FUNCTION
# ============================================================

def generate_kpi(group_columns, output_name):
    """Generate sales and profit KPIs for selected dimensions."""

    table = (
        df.groupby(group_columns, dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Quantity=("Quantity", "sum"),
            AvgDiscount=("Discount", "mean")
        )
        .round(2)
    )

    table["Margin_%"] = np.where(
        table["Sales"] != 0,
        table["Profit"] / table["Sales"] * 100,
        0
    ).round(1)

    if output_name in ["month", "year"]:
        table = table.sort_index()
    else:
        table = table.sort_values(
            "Sales",
            ascending=False
        )

    table.to_csv(
        OUTPUT_DIR / f"kpi_by_{output_name}.csv"
    )

    return table


# ============================================================
# 15. GENERATE KPI TABLES
# ============================================================

category_kpi = generate_kpi(
    "Category",
    "category"
)

subcategory_kpi = generate_kpi(
    ["Category", "Sub-Category"],
    "subcategory"
)

region_kpi = generate_kpi(
    "Region",
    "region"
)

state_kpi = generate_kpi(
    "State",
    "state"
)

segment_kpi = generate_kpi(
    "Segment",
    "segment"
)

shipmode_kpi = generate_kpi(
    "Ship Mode",
    "shipmode"
)

discount_kpi = generate_kpi(
    "DiscountBand",
    "discountband"
)

month_kpi = generate_kpi(
    "Month",
    "month"
)

year_kpi = generate_kpi(
    "Year",
    "year"
)

product_kpi = generate_kpi(
    "Product Name",
    "product"
)


# ============================================================
# 16. PRODUCT PERFORMANCE
# ============================================================

product_kpi.sort_values(
    "Profit",
    ascending=True
).head(15).to_csv(
    OUTPUT_DIR / "loss_making_products.csv"
)

product_kpi.sort_values(
    "Profit",
    ascending=False
).head(15).to_csv(
    OUTPUT_DIR / "top_profit_products.csv"
)


# ============================================================
# 17. CUSTOMER ANALYSIS
# ============================================================

customer_kpi = (
    df.groupby(
        ["Customer ID", "Customer Name"],
        dropna=False
    )
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        FirstOrder=("Order Date", "min"),
        LastOrder=("Order Date", "max")
    )
    .sort_values(
        "Sales",
        ascending=False
    )
)

customer_kpi[["Sales", "Profit"]] = (
    customer_kpi[["Sales", "Profit"]].round(2)
)

customer_kpi["RepeatCustomer"] = (
    customer_kpi["Orders"] > 1
).map({
    True: "Yes",
    False: "No"
})

customer_kpi.to_csv(
    OUTPUT_DIR / "customers.csv"
)

customer_kpi.head(20).to_csv(
    OUTPUT_DIR / "top_customers.csv"
)


# ============================================================
# 18. BUSINESS INSIGHTS
# ============================================================

def money(value):
    return f"${value:,.0f}"


def percentage(value):
    return f"{value:.1f}%"


def calculate_margin(profit, sales):
    if sales == 0:
        return 0.0

    return profit / sales * 100


total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()

overall_margin = calculate_margin(
    total_profit,
    total_sales
)

best_category = (
    category_kpi["Profit"]
    .idxmax()
)

subcategory_table = (
    subcategory_kpi
    .reset_index()
)

loss_categories = subcategory_table[
    subcategory_table["Profit"] < 0
]

high_discount = df[
    df["Discount"] > 0.20
]

low_discount = df[
    df["Discount"] <= 0.20
]

high_discount_margin = calculate_margin(
    high_discount["Profit"].sum(),
    high_discount["Sales"].sum()
)

low_discount_margin = calculate_margin(
    low_discount["Profit"].sum(),
    low_discount["Sales"].sum()
)

region_margin = region_kpi.sort_values(
    "Margin_%"
)

best_region = region_margin.index[-1]
weakest_region = region_margin.index[0]

top_state = state_kpi.index[0]

monthly_sales = (
    df.groupby(
        df["Order Date"].dt.month
    )["Sales"]
    .sum()
)

busiest_months = (
    monthly_sales
    .sort_values(ascending=False)
    .head(3)
    .index
)

MONTH_NAMES = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

yearly_sales = year_kpi["Sales"]

if len(yearly_sales) > 1:
    previous_year = yearly_sales.index[-2]
    latest_year = yearly_sales.index[-1]

    previous_sales = yearly_sales.iloc[-2]
    latest_sales = yearly_sales.iloc[-1]

    sales_growth = (
        (latest_sales - previous_sales)
        / previous_sales * 100
        if previous_sales != 0
        else 0
    )
else:
    previous_year = None
    latest_year = None
    sales_growth = None

top_ten_percent_count = max(
    1,
    int(np.ceil(len(customer_kpi) * 0.10))
)

top_customer_sales_share = (
    customer_kpi.head(top_ten_percent_count)["Sales"].sum()
    / total_sales * 100
    if total_sales != 0
    else 0
)

average_shipping_days = df["ShipDays"].mean()

insights = [
    f"# Superstore Business Insights — {SOURCE_NAME}",
    "",
    "## Headline Performance",
    f"- Total Sales: {money(total_sales)}",
    f"- Total Profit: {money(total_profit)}",
    f"- Overall Profit Margin: {percentage(overall_margin)}",
    f"- Total Orders: {df['Order ID'].nunique():,}",
    f"- Total Customers: {df['Customer ID'].nunique():,}",
    f"- Total Quantity Sold: {int(df['Quantity'].sum()):,}",
    ""
]

if sales_growth is not None:
    insights.append(
        f"- Sales Growth ({previous_year} to {latest_year}): "
        f"{sales_growth:+.1f}%"
    )

insights.extend([
    "",
    "## Key Findings",
    "",
    f"1. **Top Category:** {best_category} generated "
    f"the highest category profit "
    f"({money(category_kpi.loc[best_category, 'Profit'])}).",
    "",
    "2. **Loss-Making Sub-Categories:** "
    + (
        ", ".join(loss_categories["Sub-Category"].astype(str))
        if not loss_categories.empty
        else "No loss-making sub-categories were identified."
    ),
    "",
    f"3. **Discount Impact:** Discounts above 20% "
    f"recorded a profit margin of "
    f"{percentage(high_discount_margin)}, compared with "
    f"{percentage(low_discount_margin)} for discounts of 20% or less.",
    "",
    f"4. **Regional Profitability:** {best_region} "
    f"recorded the highest regional profit margin "
    f"({percentage(region_margin.loc[best_region, 'Margin_%'])}). "
    f"{weakest_region} recorded the lowest "
    f"({percentage(region_margin.loc[weakest_region, 'Margin_%'])}).",
    "",
    f"5. **Top State by Sales:** {top_state} generated "
    f"{money(state_kpi.loc[top_state, 'Sales'])} in sales.",
    "",
    "6. **Busiest Months:** "
    + ", ".join(
        MONTH_NAMES[int(month)]
        for month in busiest_months
    ) + ".",
    "",
    (
        f"7. **Shipping:** Average shipping time was "
        f"{average_shipping_days:.1f} days."
        if pd.notna(average_shipping_days)
        else "7. **Shipping:** Shipping time was unavailable."
    ),
    "",
    f"8. **Customer Concentration:** The top 10% of customers "
    f"accounted for {percentage(top_customer_sales_share)} "
    f"of total sales.",
    "",
    "## Business Recommendations",
    "",
    "1. Review pricing and discount practices in loss-making "
    "sub-categories to improve margins.",
    "",
    f"2. Maintain focus on profitable categories, particularly "
    f"{best_category}, while monitoring product-level performance.",
    "",
    f"3. Investigate the factors behind {weakest_region}'s "
    f"comparatively lower profit margin.",
    "",
    "4. Strengthen customer retention through targeted "
    "engagement with high-value and inactive customers.",
    ""
])

with open(
    OUTPUT_DIR / "insights.md",
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(insights))


# ============================================================
# 19. POWER BI DIMENSION TABLES
# ============================================================

def create_dimension(columns, key_name, unique_by=None):
    """Create a dimension table with a sequential surrogate key."""

    dimension = (
        df.drop_duplicates(
            subset=unique_by or columns
        )[columns]
        .reset_index(drop=True)
        .copy()
    )

    dimension.insert(
        0,
        key_name,
        range(1, len(dimension) + 1)
    )

    return dimension


dim_customer = create_dimension(
    ["Customer ID", "Customer Name", "Segment"],
    "CustomerKey",
    ["Customer ID"]
)

dim_product = create_dimension(
    ["Product ID", "Product Name", "Category", "Sub-Category"],
    "ProductKey",
    ["Product ID"]
)

dim_geo = create_dimension(
    ["Region", "State", "City"],
    "GeoKey"
)

dim_shipmode = create_dimension(
    ["Ship Mode"],
    "ShipModeKey"
)


# ============================================================
# 20. POWER BI FACT TABLE
# ============================================================

fact_sales = (
    df.merge(
        dim_customer[["CustomerKey", "Customer ID"]],
        on="Customer ID",
        how="left",
        validate="many_to_one"
    )
    .merge(
        dim_product[["ProductKey", "Product ID"]],
        on="Product ID",
        how="left",
        validate="many_to_one"
    )
    .merge(
        dim_geo,
        on=["Region", "State", "City"],
        how="left",
        validate="many_to_one"
    )
    .merge(
        dim_shipmode,
        on="Ship Mode",
        how="left",
        validate="many_to_one"
    )
)

fact_columns = [
    "Order ID",
    "Order Date",
    "Ship Date",
    "CustomerKey",
    "ProductKey",
    "GeoKey",
    "ShipModeKey",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
    "ShipDays",
    "DiscountBand",
    "Profit Status",
    "IsLossLine"
]

fact_sales[fact_columns].to_csv(
    POWERBI_DIR / "fact_sales.csv",
    index=False
)

dim_customer.to_csv(
    POWERBI_DIR / "dim_customer.csv",
    index=False
)

dim_product.to_csv(
    POWERBI_DIR / "dim_product.csv",
    index=False
)

dim_geo.to_csv(
    POWERBI_DIR / "dim_geo.csv",
    index=False
)

dim_shipmode.to_csv(
    POWERBI_DIR / "dim_shipmode.csv",
    index=False
)


# ============================================================
# 21. POWER BI DATE DIMENSION
# ============================================================

start_date = (
    df["Order Date"].min()
    .replace(month=1, day=1)
)

end_date = (
    df["Order Date"].max()
    .replace(month=12, day=31)
)

dim_date = pd.DataFrame({
    "Date": pd.date_range(
        start=start_date,
        end=end_date,
        freq="D"
    )
})

dim_date["Year"] = dim_date["Date"].dt.year

dim_date["Quarter"] = (
    "Q" + dim_date["Date"].dt.quarter.astype(str)
)

dim_date["MonthNumber"] = (
    dim_date["Date"].dt.month
)

dim_date["MonthName"] = (
    dim_date["Date"].dt.strftime("%b")
)

dim_date["YearMonth"] = (
    dim_date["Date"].dt.strftime("%Y-%m")
)

dim_date.to_csv(
    POWERBI_DIR / "dim_date.csv",
    index=False
)


# ============================================================
# 22. POWER BI DAX MEASURES
# ============================================================

dax_measures = """// FUTURE_DS_01 — Power BI Measures
// Paste each measure using Modeling > New measure.

// Core KPIs
Total Sales = SUM(fact_sales[Sales])

Total Profit = SUM(fact_sales[Profit])

Profit Margin % = DIVIDE([Total Profit], [Total Sales])

Orders = DISTINCTCOUNT(fact_sales[Order ID])

Customers = DISTINCTCOUNT(fact_sales[CustomerKey])

Quantity Sold = SUM(fact_sales[Quantity])

// Additional KPIs
Avg Order Value = DIVIDE([Total Sales], [Orders])

Avg Discount % = AVERAGE(fact_sales[Discount])

Avg Ship Days = AVERAGE(fact_sales[ShipDays])

// Time Intelligence
Sales Last Year =
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR(dim_date[Date])
)

Sales YoY % =
DIVIDE(
    [Total Sales] - [Sales Last Year],
    [Sales Last Year]
)

Profit Last Year =
CALCULATE(
    [Total Profit],
    SAMEPERIODLASTYEAR(dim_date[Date])
)

Profit YoY % =
DIVIDE(
    [Total Profit] - [Profit Last Year],
    ABS([Profit Last Year])
)

// Profitability Analysis
Loss Making Lines =
CALCULATE(
    COUNTROWS(fact_sales),
    fact_sales[Profit] < 0
)

Loss Line % =
DIVIDE(
    [Loss Making Lines],
    COUNTROWS(fact_sales)
)

Sales Share % =
DIVIDE(
    [Total Sales],
    CALCULATE(
        [Total Sales],
        ALL(dim_product)
    )
)

Profit Color =
IF(
    [Total Profit] < 0,
    "#C0392B",
    "#1F6F5C"
)
"""

with open(
    POWERBI_DIR / "measures.dax",
    "w",
    encoding="utf-8"
) as file:
    file.write(dax_measures)


# ============================================================
# 23. PREPARE INTERACTIVE WEB DASHBOARD DATA
# ============================================================

top_products = (
    df.groupby("Product Name")["Sales"]
    .sum()
    .nlargest(300)
    .index
)

df["P2"] = df["Product Name"].where(
    df["Product Name"].isin(top_products),
    "Other products"
)

df["FirstLine"] = (
    ~df.duplicated("Order ID")
).astype(int)

dashboard_data = (
    df.groupby(
        [
            "Month",
            "Region",
            "Category",
            "Segment",
            "P2",
            "Discount"
        ],
        dropna=False
    )
    .agg(
        s=("Sales", "sum"),
        p=("Profit", "sum"),
        q=("Quantity", "sum"),
        n=("FirstLine", "sum")
    )
    .reset_index()
)

dashboard_rows = [
    [
        row.Month,
        row.Region,
        row.Category,
        row.Segment,
        row.P2,
        round(row.s),
        round(row.p),
        int(row.q),
        round(float(row.Discount), 2),
        int(row.n)
    ]
    for row in dashboard_data.itertuples()
]

dashboard_cleaning = {
    "raw_rows": cleaning_report["raw_rows"],
    "duplicates_removed": cleaning_report["duplicates_removed"],
    "bad_dates_dropped": cleaning_report["bad_dates_dropped"],
    "negative_quantity_dropped": cleaning_report["bad_quantity_dropped"],
    "sales_recalculated": 0,
    "missing_region_labelled": cleaning_report["missing_region_labelled"],
    "clean_rows": cleaning_report["clean_rows"],
    "has_profit": True
}

template_path = DASHBOARD_DIR / "template.html"

if not template_path.exists():
    raise SystemExit(
        "ERROR: dashboard/template.html was not found.\n"
        "Restore the dashboard template before running the analysis."
    )

template = template_path.read_text(
    encoding="utf-8"
)

dashboard_payload = {
    "rows": dashboard_rows,
    "cleaning": dashboard_cleaning,
    "source": SOURCE_NAME,
    "cur": "$"
}

html = template.replace(
    "__DATA__",
    json.dumps(
        dashboard_payload,
        separators=(",", ":")
    )
)

(DASHBOARD_DIR / "index.html").write_text(
    html,
    encoding="utf-8"
)


# ============================================================
# 24. FINAL VALIDATION AND SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("ANALYSIS COMPLETED")
print("=" * 60)

print(f"Source dataset: {SOURCE_NAME}")
print(f"Original rows: {raw_rows:,}")
print(f"Cleaned rows: {len(df):,}")
print(f"Unique orders: {df['Order ID'].nunique():,}")
print(f"Unique customers: {df['Customer ID'].nunique():,}")
print(f"Total quantity: {int(df['Quantity'].sum()):,}")

print("\nBUSINESS KPIs")
print("-" * 40)
print(f"Total Sales:  ${total_sales:,.2f}")
print(f"Total Profit: ${total_profit:,.2f}")
print(f"Profit Margin: {overall_margin:.2f}%")

print("\nGENERATED OUTPUTS")
print("-" * 40)
print("outputs/cleaned_superstore.csv")
print("outputs/cleaning_report.json")
print("outputs/insights.md")
print("outputs/kpi_by_*.csv")
print("outputs/customers.csv")
print("outputs/top_customers.csv")
print("outputs/loss_making_products.csv")
print("outputs/top_profit_products.csv")
print("powerbi/fact_sales.csv")
print("powerbi/dim_*.csv")
print("powerbi/measures.dax")
print("dashboard/index.html")

print("\nNo simulated data was used.")
print("Review the generated files before submission.")
print("=" * 60)
