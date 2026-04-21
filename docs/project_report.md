# End-to-End Procure-to-Pay (P2P) Analytics System
## Capstone Project Report

**Author:** [Your Name]  
**Date:** 2024  
**Technologies:** Python | Power BI | SAP BDC Concepts | Pandas | Matplotlib  
**Domain:** SAP MM + FI | Procurement Analytics | Business Intelligence  

---

## 1. EXECUTIVE SUMMARY

This capstone project presents a complete End-to-End Procure-to-Pay (P2P) Analytics System that simulates SAP MM (Materials Management) and FI (Financial Accounting) business processes. The system ingests raw procurement data, processes and transforms it using Python, computes critical KPIs, performs advanced analytics including vendor risk scoring and delay prediction, and visualizes results in an interactive Power BI dashboard.

The project demonstrates end-to-end data engineering and business intelligence capabilities aligned with SAP Business Data Cloud (SAP BDC) architecture principles, including SAP Datasphere for data integration and SAP Analytics Cloud (SAC) for visual analytics.

---

## 2. PROBLEM STATEMENT

Organizations running SAP ERP systems generate enormous volumes of procurement transaction data daily. However, much of this data remains siloed across SAP modules — Purchase Orders in MM, Invoices in FI, and Payments in FI-AP. Without proper integration and analysis, companies face:

- **Lack of visibility** into end-to-end procurement cycle performance
- **Inability to identify** underperforming or high-risk vendors proactively
- **Missing early warning signals** for delivery delays and payment risks
- **No unified KPI framework** connecting procurement operations to financial outcomes
- **Missed cost savings** from early payment discounts not being tracked

This project solves these problems by building a unified analytics system that bridges the gap between raw transaction data and actionable business intelligence.

---

## 3. SOLUTION ARCHITECTURE

### 3.1 Data Flow (End-to-End)

```
SAP Source Systems (Simulated)
        │
        ▼
 Raw CSV Datasets (5 tables)
        │
        ▼
 Python Data Pipeline
 ├── Script 1: Dataset Generation (simulate SAP extracts)
 ├── Script 2: Data Cleaning & Merging (SAP Datasphere equivalent)
 ├── Script 3: KPI Calculation Engine
 ├── Script 4: Advanced Analytics (Risk + Trend + Prediction)
 └── Script 5: Chart Generation
        │
        ▼
 Final Master Dataset + KPI Files
        │
        ▼
 Power BI Dashboard (SAP SAC equivalent)
        │
        ▼
 Business Insights & Recommendations
```

### 3.2 SAP BDC Mapping

| Project Component          | SAP BDC Equivalent                         |
|----------------------------|--------------------------------------------|
| Vendor Master CSV          | SAP MM Vendor Master (XK01)               |
| Purchase Orders CSV        | SAP ME21N Purchase Order                  |
| Goods Receipts CSV         | SAP MIGO (Movement Type 101)              |
| Invoices CSV               | SAP MIRO Invoice Verification             |
| Payments CSV               | SAP F110 Payment Run                      |
| Python merge script        | SAP Datasphere Data Flow / Transformation |
| KPI calculations           | SAP SAC Calculated Measures               |
| Power BI Dashboard         | SAP Analytics Cloud Story                 |
| Vendor Risk Scoring        | SAP Supplier Risk Management              |

---

## 4. DATASET DESCRIPTION

The project uses 5 interconnected datasets simulating SAP transactional data:

### 4.1 Vendors (20 records, 10 columns)
Represents the Vendor Master — a list of all authorized suppliers.

| Column          | Business Meaning                                      |
|-----------------|-------------------------------------------------------|
| VendorID        | Unique identifier (like SAP Vendor Account Number)    |
| VendorName      | Supplier company name                                 |
| Country         | Supplier's country (used for geo analytics)           |
| Category        | Type of goods/services supplied                       |
| PaymentTerms    | Agreed payment terms (NET30, NET45, etc.)             |
| Rating          | Internal vendor rating out of 5.0                    |
| IsActive        | Whether vendor is currently active                    |
| CreditLimit     | Maximum credit extended to vendor                     |
| OnboardingDate  | Date vendor was approved                              |

### 4.2 Purchase Orders (300 records, 13 columns)
Each row is one PO line — a formal request to buy from a vendor.

| Column           | Business Meaning                                     |
|------------------|------------------------------------------------------|
| POID             | Purchase Order number (like SAP PO number)           |
| VendorID         | Links to Vendor Master (foreign key)                 |
| Material         | What is being purchased                              |
| Department       | Internal department making the purchase              |
| Quantity         | How many units ordered                               |
| UnitPrice        | Price per unit                                       |
| TotalAmount      | Quantity × UnitPrice = total PO value                |
| PODate           | Date PO was created                                  |
| ExpectedDelivery | Promised delivery date from vendor                   |
| POStatus         | Approved / Pending / Cancelled                       |

### 4.3 Goods Receipts (166 records, 10 columns)
Confirmation that goods were physically received and checked.

| Column            | Business Meaning                                    |
|-------------------|-----------------------------------------------------|
| GRID              | Goods Receipt document number                       |
| POID              | Links back to Purchase Order                        |
| ReceivedDate      | Actual date goods arrived at warehouse              |
| ReceivedQuantity  | How many units actually arrived                     |
| InspectionResult  | Quality check result: Passed / Failed / Partial     |

### 4.4 Invoices (166 records, 12 columns)
Bills sent by vendors after delivering goods.

| Column        | Business Meaning                                        |
|---------------|---------------------------------------------------------|
| InvoiceID     | Unique invoice number                                   |
| InvoiceAmount | Net amount (before tax)                                 |
| TaxAmount     | GST/VAT (18% applied)                                  |
| TotalPayable  | Final amount to be paid                                 |
| DueDate       | Last date for payment                                   |
| InvoiceStatus | Approved / Pending / Disputed                           |

### 4.5 Payments (93 records, 11 columns)
Records of actual money transferred to vendors.

| Column        | Business Meaning                                        |
|---------------|---------------------------------------------------------|
| PaymentID     | Unique payment document number                          |
| PaymentDate   | Actual date payment was made                            |
| AmountPaid    | Actual amount paid (may differ if discount applied)     |
| DiscountTaken | Early payment discount captured                         |
| PaymentMethod | Bank Transfer / Cheque / ACH / Wire                     |

---

## 5. KPI FRAMEWORK

### KPI 1: Total Spend Analysis
- **Definition:** Sum of all Purchase Order values
- **Formula:** `SUM(TotalAmount)` across all approved POs
- **Result:** $208.3M total procurement spend over 2 years
- **Business Use:** Budget monitoring, spend by category prioritization

### KPI 2: Vendor Performance Score
- **Definition:** Composite score measuring vendor reliability
- **Formula:**
  ```
  Score = (OnTimeDelivery% × 0.40) + (FulfillmentRate × 0.30) +
          (InspectionPass% × 0.20) + (Rating/5×100 × 0.10)
  ```
- **Result:** Average vendor score of 66.1/100 (room for improvement)
- **Business Use:** Vendor review meetings, contract renewal decisions

### KPI 3: On-Time Delivery Rate
- **Definition:** % of deliveries that arrived on or before expected date
- **Formula:** `(On-Time Deliveries / Total Deliveries) × 100`
- **Result:** 33.1% on-time (66.9% of deliveries were late)
- **Business Use:** Vendor performance reviews, SLA enforcement

### KPI 4: Days Payable Outstanding (DPO)
- **Definition:** Average days taken from PO to payment
- **Formula:** `AVG(PaymentDate - PODate)`
- **Result:** 91.4 days average procurement cycle
- **Business Use:** Working capital management, cash flow planning

### KPI 5: Procurement Cycle Time
- **Definition:** End-to-end time from PO creation to payment
- **Breakdown:**
  - PO → Delivery: 32.7 days
  - Delivery → Invoice: 5.5 days
  - Invoice → Payment: 7.1 days
- **Business Use:** Process bottleneck identification

---

## 6. ADVANCED ANALYTICS

### 6.1 Vendor Risk Scoring
A multi-dimensional risk assessment framework scoring vendors across:
- **Delivery Risk (30%):** Historical late delivery rate
- **Fulfillment Risk (20%):** How consistently full quantities are delivered
- **Invoice Dispute Risk (20%):** Frequency of billing disputes
- **Quality Risk (20%):** Inspection failure rate
- **Concentration Risk (10%):** Over-dependence on single vendor

**Output:** Each vendor receives a Risk Tier: 🔴 High / 🟡 Medium / 🟢 Low

### 6.2 Spend Trend Analysis
- Month-over-Month (MoM) growth calculation
- 3-Month Rolling Average smoothing
- Year-over-Year (YoY) comparison
- Statistical anomaly detection (±2 standard deviations)
- Category-level trend decomposition

**Key Finding:** Spend trend is increasing (+trend), with 1 anomalous spike month identified.

### 6.3 Delivery Delay Prediction (Rule-Based)
A rule-based scoring model that predicts delay risk for any new PO:
- **Factor 1 (40pts):** Vendor's historical late delivery rate
- **Factor 2 (25pts):** Lead time risk (too short or too long)
- **Factor 3 (20pts):** Order quantity risk
- **Factor 4 (15pts):** Category's average delay profile

**Model Accuracy:** 62.7% (validated against actual delivery data)  
**Practical Use:** Flag high-risk POs for proactive follow-up with vendors

---

## 7. POWER BI DASHBOARD GUIDE

### 7.1 Import Instructions
1. Open Power BI Desktop
2. Click **Home → Get Data → Text/CSV**
3. Import these files from `/data/final/` and `/outputs/kpis/`:
   - `p2p_master_dataset.csv` (main table)
   - `kpi2_vendor_performance.csv`
   - `vendor_risk_scores.csv`
   - `spend_trend_analysis.csv`
4. In **Model View**, create relationships:
   - `p2p_master_dataset[VendorID]` → `kpi2_vendor_performance[VendorID]`

### 7.2 Dashboard Pages

**Page 1: Executive Summary**
- 8 KPI Cards: Total Spend, Paid, Vendor Score, On-Time %, etc.
- Donut Chart: Spend by Category
- Line Chart: Monthly Spend Trend
- Bar Chart: Top 10 Vendors by Spend

**Page 2: Vendor Performance**
- Bar Chart: Vendor Score Rankings
- Table: Full Vendor Scorecard (Score, Tier, Delay, Fulfillment)
- Scatter Chart: Risk Map (Spend vs Risk Score)
- Slicer: Filter by Category, Country

**Page 3: Delivery & Payment**
- Pie Chart: Delivery Delay Distribution
- Bar Chart: Avg Delay by Vendor
- Gauge: On-Time Delivery Rate (target: 85%)
- Line Chart: Payment Delay Trend

**Page 4: Predictive Insights**
- Bar Chart: High/Medium/Low Risk PO counts
- Table: Top 20 High-Risk POs
- Trend: Spend anomaly detection chart

### 7.3 Key DAX Measures
```DAX
-- Total Spend
Total Spend = SUM(p2p_master_dataset[TotalAmount])

-- On-Time Delivery Rate
OTD Rate = 
DIVIDE(
    COUNTX(p2p_master_dataset, IF([DeliveryDelayDays] <= 0, 1)),
    COUNT(p2p_master_dataset[POID])
) * 100

-- Average Procurement Cycle
Avg Cycle Days = AVERAGE(p2p_master_dataset[ProcurementCycleTime])

-- Late Payment % 
Late Payment % = 
DIVIDE(
    COUNTX(p2p_master_dataset, IF([IsLatePayment] = 1, 1)),
    COUNT(p2p_master_dataset[POID])
) * 100

-- Discounts Missed (opportunity cost)
Discounts Missed = 
SUMX(
    FILTER(p2p_master_dataset, [PaymentTerms] = "2/10NET30" && [DiscountTaken] = 0),
    [TotalPayable] * 0.02
)
```

---

## 8. KEY BUSINESS INSIGHTS

Based on the analysis, the following insights were identified:

1. **📦 Packaging & Electronics** account for 25.7% of total spend — strategic sourcing review recommended.

2. **🚚 Late Delivery Crisis:** 66.9% of deliveries are late, averaging 6.5 days delay. This significantly impacts production planning and customer commitments.

3. **💰 Discount Leakage:** $427,716 in potential early payment discounts were missed. Automating payment runs for 2/10NET30 vendors would capture this.

4. **⚠️ Vendor Concentration Risk:** A few vendors account for a disproportionate share of spend. Diversification strategy should be considered.

5. **🔄 Cycle Time Bottleneck:** The PO-to-Delivery stage (32.7 days) is the biggest bottleneck in the 91-day cycle. Supplier communication improvements could cut this significantly.

6. **📈 Spend Growth:** Overall spend trend is increasing, suggesting company growth — procurement strategy should plan for volume scaling.

---

## 9. TECH STACK

| Layer              | Technology                    | Purpose                         |
|--------------------|-------------------------------|---------------------------------|
| Data Generation    | Python 3.12 + Faker           | Simulate SAP extracts           |
| Data Processing    | Pandas, NumPy                 | ETL pipeline                    |
| Visualization (Py) | Matplotlib, Seaborn           | Chart generation                |
| Dashboard          | Microsoft Power BI Desktop    | Interactive BI dashboard        |
| Documentation      | Markdown + PDF                | Project report                  |
| Version Control    | Git + GitHub                  | Code repository                 |
| Concepts Applied   | SAP MM, FI, BDC, Datasphere   | Business domain knowledge       |

---

## 10. UNIQUE PROJECT FEATURES

1. **End-to-End SAP P2P Simulation** — Covers all 5 SAP transaction types
2. **Composite Vendor Risk Score** — Multi-dimensional, weighted scoring model
3. **Rule-Based ML-Style Prediction** — Delay risk prediction without complex ML libraries
4. **Statistical Anomaly Detection** — Identifies unusual spend patterns automatically
5. **Discount Leakage Quantification** — Calculates actual missed financial opportunity
6. **Stage-Level Cycle Decomposition** — Breaks cycle time into 3 operational stages
7. **SAP BDC Architecture Alignment** — Maps to real SAP enterprise architecture

---

## 11. FUTURE SCOPE

1. **Machine Learning Integration:** Replace rule-based delay prediction with scikit-learn Random Forest model for higher accuracy.

2. **SAP BTP Connection:** Use SAP BTP OData APIs to pull live data from real SAP systems instead of simulated CSVs.

3. **Real-Time Dashboard:** Integrate with SAP Analytics Cloud for live refresh via SAP Datasphere data flows.

4. **NLP Dispute Analysis:** Apply NLP to invoice dispute comments to classify dispute root causes automatically.

5. **Spend Forecasting:** Implement time-series forecasting (ARIMA/Prophet) for budget planning.

6. **Supplier Portal Simulation:** Build a web app (Flask/Streamlit) where suppliers can view their own performance scores.

---

## 12. CONCLUSION

This project demonstrates a complete, production-grade approach to P2P analytics using SAP-aligned concepts. By combining Python data engineering, statistical analysis, advanced risk scoring, and Power BI visualization, it delivers actionable intelligence that can directly impact procurement decisions, vendor relationship management, and financial outcomes.

The project is structured for real-world deployment and can be extended to integrate with live SAP systems via SAP Business Data Cloud (BDC) and SAP Datasphere.

---

*[Insert Power BI dashboard screenshots here]*  
*[Insert GitHub repository link here]*
