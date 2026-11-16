# Power BI guide for Superstore (plain steps, about 45 minutes)

Do the parts in order. Tick each step off as you go.

## Part A: Bring the data in
| Step | What to do | Meaning |
|---|---|---|
| 1 | Open Power BI Desktop (free, Windows). Home > **Get data** > **Text/CSV** | Starts loading a file |
| 2 | Pick `powerbi/fact_sales.csv` > **Load**. Repeat for `dim_customer`, `dim_product`, `dim_geo`, `dim_shipmode`, `dim_date` | Loads all 6 files (one big table plus 5 small lookup tables) |

## Part B: Connect the tables
| Step | What to do | Meaning |
|---|---|---|
| 1 | Click the **Model** icon (left side, 3rd icon) | The picture of your tables |
| 2 | Drag `CustomerKey` from `fact_sales` onto `CustomerKey` in `dim_customer`. Do the same for `ProductKey`, `GeoKey`, `ShipModeKey` | Joins each lookup table to the big one |
| 3 | Drag `Order Date` (fact_sales) onto `Date` (dim_date) | Lets you filter by year and month |
| 4 | Click `dim_date` > Table tools > **Mark as date table** > choose `Date` | Makes year-by-year comparisons work |

## Part C: Add the formulas
Open `powerbi/measures.dax`. For each line: Home > **New measure**, paste the line, press Enter.
(17 lines in total. They give you Total Sales, Total Profit, Profit Margin %, and so on.)

## Part D: Build 4 pages
Page = a tab at the bottom. Click **+** for a new one.

**Page 1: Overview**
| Visual | Fields | Meaning |
|---|---|---|
| 6 Cards | Total Sales, Total Profit, Profit Margin %, Orders, Customers, Sales YoY % | Headline numbers |
| Line chart | X: `dim_date[YearMonth]`, Y: Total Sales | Sales over time |
| Column chart | X: `dim_date[Year]`, Y: Total Sales and Total Profit | Year by year |
| Slicers (filter buttons) | `dim_date[Year]`, `dim_geo[Region]`, `dim_product[Category]` | Lets people filter |

**Page 2: Products and Profit**
| Visual | Fields | Meaning |
|---|---|---|
| Bar chart | Axis: `dim_product[Sub-Category]`, Values: Total Profit | Shows which sub-categories lose money |
| Make losses red | Select the bar chart > Format > Bars > Colors > **fx** > Format style: Field value > Based on: Profit Color | Red = losing money, green = making money |
| Bar chart | Axis: `dim_product[Product Name]`, Values: Total Sales, filter to Top 10 (Filters pane > Top N) | Best sellers |
| Column chart | Axis: `fact_sales[DiscountBand]`, Values: Profit Margin % | Shows that big discounts destroy profit |

**Page 3: Regions and Customers**
| Visual | Fields | Meaning |
|---|---|---|
| Map (or bar chart) | Location: `dim_geo[State]`, Size: Total Sales | Where sales come from |
| Column chart | Axis: `dim_geo[Region]`, Values: Total Sales, Profit Margin % | Best and weakest regions |
| Table | `dim_customer[Customer Name]`, Total Sales, Total Profit. Filter Top 10 by Total Sales | Biggest customers |
| Column chart | Axis: `dim_shipmode[Ship Mode]`, Values: Avg Ship Days | Delivery speed |

**Page 4: Insights and Actions**
Add a Text box (Insert > Text box). Copy the 8 findings and 4 recommendations from `outputs/insights.md` (they are written for you).

## Part E: Check your numbers (real Kaggle file)
| Card | Should be about | Meaning |
|---|---|---|
| Total Sales | $2,297,201 | If it matches, your data loaded correctly |
| Total Profit | $286,397 | Same check |
| Customers | 793 | Same check |
| Quantity Sold | 37,873 | Same check |

If a number is far off, you probably have the wrong table connected. Check Part B.

## Part F: Finish
1. Format: set one font, add a title on each page ("Superstore Sales Performance").
2. File > **Save as** `FUTURE_DS_01.pbix`.
3. File > Export > **Export to PDF**.
4. Take 3 screenshots (one per page).
5. Put the `.pbix`, the PDF and the screenshots in a `report/` folder of your repo.
