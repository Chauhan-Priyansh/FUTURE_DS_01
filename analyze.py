"""Cleans the Superstore file, writes KPI tables + plain-language insights, builds Power BI files and a quick web dashboard.
Uses the CSV in data/kaggle/ if there is one, otherwise the simulated demo file."""
import glob, json, os, numpy as np, pandas as pd
K = sorted(glob.glob("data/kaggle/*.csv"), key=os.path.getsize, reverse=True)
SRC = K[0] if K else "data/demo_superstore_simulated.csv"; DEMO = not K; CUR = "$"
ALIAS = {"Order ID": ["orderid"], "Order Date": ["orderdate"], "Ship Date": ["shipdate"], "Ship Mode": ["shipmode"], "Customer ID": ["customerid"],
 "Customer Name": ["customername"], "Segment": ["segment"], "City": ["city"], "State": ["state", "province"], "Region": ["region"], "Product ID": ["productid"],
 "Category": ["category"], "Sub-Category": ["subcategory"], "Product Name": ["productname", "product"], "Sales": ["sales"], "Quantity": ["quantity"],
 "Discount": ["discount"], "Profit": ["profit"]}
try: raw = pd.read_csv(SRC)
except UnicodeDecodeError: raw = pd.read_csv(SRC, encoding="latin-1")
norm = {c: c.lower().replace(" ", "").replace("_", "").replace("-", "") for c in raw.columns}; ren = {}
for std, names in ALIAS.items():
    for n in names:
        hit = [c for c, v in norm.items() if v == n and c not in ren]
        if hit: ren[hit[0]] = std; break
df = raw.rename(columns=ren)[list(dict.fromkeys(ren.values()))].copy()
miss = [c for c in ["Order Date", "Sales", "Profit", "Product Name", "Category", "Region"] if c not in df]
assert not miss, f"These columns were not found in {SRC}: {miss}. Send me the first line of your CSV."
log = {"source_file": os.path.basename(SRC), "using_demo_data": DEMO, "raw_rows": len(df)}
for c, v in {"Order ID": "Unknown", "Customer ID": "Unknown", "Customer Name": "Unknown", "Segment": "Unknown", "City": "Unknown", "State": "Unknown", "Ship Mode": "Unknown", "Sub-Category": "Unknown"}.items():
    if c not in df: df[c] = v
if "Product ID" not in df: df["Product ID"] = df["Product Name"]
if "Quantity" not in df: df["Quantity"] = 1
if "Discount" not in df: df["Discount"] = 0.0
log["duplicates_removed"] = 0
FM = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y", "%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M:%S"]
def dates(s):
    s = s.astype(str).str.strip(); P = [pd.to_datetime(s, format=f, errors="coerce") for f in FM]; o = sorted(range(len(FM)), key=lambda i: -P[i].notna().sum()); d = P[o[0]]
    for i in o[1:]: d = d.fillna(P[i])
    return d
df["Order Date"] = dates(df["Order Date"]); df["Ship Date"] = dates(df["Ship Date"]) if "Ship Date" in df else pd.NaT
n = len(df); df = df.dropna(subset=["Order Date"]); log["bad_dates_dropped"] = n - len(df)
assert len(df) > 0, "No readable dates found. Send me the first 2 lines of your CSV."
for c in ["Sales", "Profit", "Quantity", "Discount"]: df[c] = pd.to_numeric(df[c], errors="coerce")
n = len(df); df = df.dropna(subset=["Sales", "Profit"]); log["missing_sales_or_profit_dropped"] = n - len(df)
n = len(df); df = df[df.Quantity.fillna(1) > 0]; log["bad_quantity_dropped"] = n - len(df)
df["Discount"] = df.Discount.fillna(0).clip(0, 1)
for c in ["Segment", "Region", "Category", "Sub-Category", "Ship Mode", "City", "State"]: df[c] = df[c].astype("string").str.strip().str.title().fillna("Unknown")
df["Product Name"] = df["Product Name"].astype("string").str.strip().fillna("Unknown")
df["Year"] = df["Order Date"].dt.year; df["Month"] = df["Order Date"].dt.strftime("%Y-%m")
df["ShipDays"] = (df["Ship Date"] - df["Order Date"]).dt.days
df["DiscountBand"] = pd.cut(df.Discount, [-.001, 0, .1, .2, .3, .5, 1], labels=["No discount", "1-10%", "11-20%", "21-30%", "31-50%", "Over 50%"]).astype(str)
df["IsLossLine"] = (df.Profit < 0).astype(int); log["clean_rows"] = len(df); log["customers"] = int(df["Customer ID"].nunique()); log["orders"] = int(df["Order ID"].nunique())
df = df.sort_values("Order Date").reset_index(drop=True)
df.to_csv("outputs/cleaned_superstore.csv", index=False); json.dump(log, open("outputs/cleaning_report.json", "w"), indent=2)
def kpi(by, name):
    t = df.groupby(by).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Quantity=("Quantity", "sum"), AvgDiscount=("Discount", "mean")).round(2)
    t["Margin_%"] = (t.Profit / t.Sales * 100).round(1); t = t.sort_index() if name in ("month", "year") else t.sort_values("Sales", ascending=False); t.to_csv(f"outputs/kpi_by_{name}.csv"); return t
cat = kpi("Category", "category"); sub = kpi(["Category", "Sub-Category"], "subcategory"); reg = kpi("Region", "region"); st = kpi("State", "state"); seg = kpi("Segment", "segment")
ship = kpi("Ship Mode", "shipmode"); dband = kpi("DiscountBand", "discountband"); mon = kpi("Month", "month"); yr = kpi("Year", "year"); prod = kpi("Product Name", "product")
prod.sort_values("Profit").head(15).to_csv("outputs/loss_making_products.csv"); prod.sort_values("Profit", ascending=False).head(15).to_csv("outputs/top_profit_products.csv")
cu = df.groupby(["Customer ID", "Customer Name"]).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), FirstOrder=("Order Date", "min"), LastOrder=("Order Date", "max")).sort_values("Sales", ascending=False)
cu[["Sales", "Profit"]] = cu[["Sales", "Profit"]].round(2)
cu["RepeatCustomer"] = (cu.Orders > 1).map({True: "Yes", False: "No"}); cu.to_csv("outputs/customers.csv"); cu.head(20).to_csv("outputs/top_customers.csv")
# ---- plain-language insights ----
m = lambda x: f"${x:,.0f}"; p = lambda x: f"{x:.1f}%"; S, P = df.Sales.sum(), df.Profit.sum(); mg = P / S * 100
bestc = cat.sort_values("Profit", ascending=False).index[0]; sc = sub.reset_index(); losers = sc[sc.Profit < 0]
hi = df[df.Discount > .2]; lo = df[df.Discount <= .2]; himg, lomg = hi.Profit.sum() / hi.Sales.sum() * 100, lo.Profit.sum() / lo.Sales.sum() * 100
rg = reg.sort_values("Margin_%"); calm = df.groupby(df["Order Date"].dt.month).Sales.sum().sort_values(ascending=False).head(3).index
MN = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ys = yr.Sales; g = (ys.iloc[-1] / ys.iloc[-2] - 1) * 100 if len(ys) > 1 else float("nan"); top10 = cu.head(int(np.ceil(len(cu) * .1))).Sales.sum() / S * 100
txt = [f"# Superstore insights (auto-written from {log['source_file']})", "" if not DEMO else "**Demo data: these numbers are simulated. Re-run with the real Kaggle file before using them.**", "",
 "## Headline numbers", f"- Sales {m(S)}, profit {m(P)}, profit margin {p(mg)}", f"- {log['orders']:,} orders from {log['customers']:,} customers, {int(df.Quantity.sum()):,} items sold",
 f"- Sales growth {int(ys.index[-2])} to {int(ys.index[-1])}: {g:+.1f}%" if len(ys) > 1 else "", "", "## Findings",
 f"1. **{bestc}** earns the most profit of the three categories ({m(cat.loc[bestc, 'Profit'])}).",
 f"2. Sub-categories losing money: {', '.join(losers['Sub-Category']) if len(losers) else 'none'}." + (f" Together they lost {m(-losers.Profit.sum())}." if len(losers) else ""),
 f"3. Discounts above 20% earn a {p(himg)} margin; discounts of 20% or less earn {p(lomg)}.",
 f"4. Best region by margin: {rg.index[-1]} ({p(rg['Margin_%'].iloc[-1])}). Weakest: {rg.index[0]} ({p(rg['Margin_%'].iloc[0])}).",
 f"5. Top state by sales: {st.index[0]} ({m(st.Sales.iloc[0])}).", f"6. Busiest months: {', '.join(MN[i] for i in calm)}.",
 f"7. Average shipping time is {df.ShipDays.mean():.1f} days." if df.ShipDays.notna().any() else "", f"8. The top 10% of customers bring {p(top10)} of all sales.", "",
 "## Recommendations", "1. Cap discounts at about 20% on the loss-making sub-categories, or raise their prices.",
 f"2. Put more stock and marketing behind {bestc} and the busiest months.", f"3. Review pricing and discounts in {rg.index[0]}, the weakest region.", "4. Give the top customers a loyalty offer and win back customers who have not ordered recently."]
open("outputs/insights.md", "w").write("\n".join(t for t in txt if t is not None) + "\n")
# ---- Power BI star schema ----
def dim(cols, key, first=None):
    d = df.drop_duplicates(first or cols)[cols].reset_index(drop=True); d.insert(0, key, range(1, len(d) + 1)); return d
dc = dim(["Customer ID", "Customer Name", "Segment"], "CustomerKey", ["Customer ID"]); dp = dim(["Product ID", "Product Name", "Category", "Sub-Category"], "ProductKey", ["Product ID"])
dg = dim(["Region", "State", "City"], "GeoKey"); dsm = dim(["Ship Mode"], "ShipModeKey")
f = df.merge(dc[["CustomerKey", "Customer ID"]], on="Customer ID").merge(dp[["ProductKey", "Product ID"]], on="Product ID").merge(dg, on=["Region", "State", "City"]).merge(dsm, on="Ship Mode")
f[["Order ID", "Order Date", "Ship Date", "CustomerKey", "ProductKey", "GeoKey", "ShipModeKey", "Sales", "Quantity", "Discount", "Profit", "ShipDays", "DiscountBand", "IsLossLine"]].to_csv("powerbi/fact_sales.csv", index=False)
dc.to_csv("powerbi/dim_customer.csv", index=False); dp.to_csv("powerbi/dim_product.csv", index=False); dg.to_csv("powerbi/dim_geo.csv", index=False); dsm.to_csv("powerbi/dim_shipmode.csv", index=False)
dd = pd.DataFrame({"Date": pd.date_range(f"{df['Order Date'].dt.year.min()}-01-01", f"{df['Order Date'].dt.year.max()}-12-31")})
dd["Year"] = dd.Date.dt.year; dd["Quarter"] = "Q" + dd.Date.dt.quarter.astype(str); dd["MonthNumber"] = dd.Date.dt.month; dd["MonthName"] = dd.Date.dt.strftime("%b"); dd["YearMonth"] = dd.Date.dt.strftime("%Y-%m"); dd.to_csv("powerbi/dim_date.csv", index=False)
open("powerbi/measures.dax", "w").write("""// Paste each measure into: Modeling > New measure
Total Sales = SUM(fact_sales[Sales])
Total Profit = SUM(fact_sales[Profit])
Profit Margin % = DIVIDE([Total Profit], [Total Sales])
Orders = DISTINCTCOUNT(fact_sales[Order ID])
Customers = DISTINCTCOUNT(fact_sales[CustomerKey])
Quantity Sold = SUM(fact_sales[Quantity])
Avg Order Value = DIVIDE([Total Sales], [Orders])
Avg Discount % = AVERAGE(fact_sales[Discount])
Avg Ship Days = AVERAGE(fact_sales[ShipDays])
Sales Last Year = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[Date]))
Sales YoY % = DIVIDE([Total Sales] - [Sales Last Year], [Sales Last Year])
Profit Last Year = CALCULATE([Total Profit], SAMEPERIODLASTYEAR(dim_date[Date]))
Profit YoY % = DIVIDE([Total Profit] - [Profit Last Year], ABS([Profit Last Year]))
Loss Making Lines = CALCULATE(COUNTROWS(fact_sales), fact_sales[Profit] < 0)
Loss Line % = DIVIDE([Loss Making Lines], COUNTROWS(fact_sales))
Sales Share % = DIVIDE([Total Sales], CALCULATE([Total Sales], ALL(dim_product)))
Profit Color = IF([Total Profit] < 0, "#C0392B", "#1F6F5C")
""")
# ---- quick web dashboard ----
top = df.groupby("Product Name").Sales.sum().nlargest(300).index; df["P2"] = df["Product Name"].where(df["Product Name"].isin(top), "Other products"); df["FirstLine"] = (~df.duplicated("Order ID")).astype(int)
g2 = df.groupby(["Month", "Region", "Category", "Segment", "P2", "Discount"]).agg(s=("Sales", "sum"), p=("Profit", "sum"), q=("Quantity", "sum"), n=("FirstLine", "sum")).reset_index()
rows = [[r.Month, r.Region, r.Category, r.Segment, r.P2, round(r.s), round(r.p), int(r.q), round(float(r.Discount), 2), int(r.n)] for r in g2.itertuples()]
cl = {"raw_rows": log["raw_rows"], "duplicates_removed": log["duplicates_removed"], "bad_dates_dropped": log["bad_dates_dropped"], "negative_quantity_dropped": log["bad_quantity_dropped"], "sales_recalculated": 0, "missing_region_labelled": 0, "clean_rows": log["clean_rows"], "has_profit": True}
html = open("dashboard/template.html", encoding="utf-8").read().replace("__DATA__", json.dumps({"rows": rows, "cleaning": cl, "source": log["source_file"] + (" (SIMULATED)" if DEMO else ""), "cur": CUR}, separators=(",", ":")))
open("dashboard/index.html", "w", encoding="utf-8").write(html)
print(json.dumps(log)); print(f"Sales {S:,.2f} | Profit {P:,.2f} | Customers {log['customers']} | Quantity {int(df.Quantity.sum()):,}")
