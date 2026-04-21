# 🏭 End-to-End Procure-to-Pay (P2P) Analytics System
### SAP Business Data Cloud Concepts | Python | Power BI | Business Intelligence

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Power BI](https://img.shields.io/badge/PowerBI-Dashboard-yellow?logo=powerbi)
![SAP](https://img.shields.io/badge/SAP-BDC%20Concepts-blue?logo=sap)
![Status](https://img.shields.io/badge/Status-Completed-green)

---

## 📌 Project Overview

A comprehensive end-to-end analytics system that simulates **SAP MM + FI Procure-to-Pay processes** and delivers actionable procurement intelligence through Python analytics and Power BI dashboards.

This project is aligned with **SAP Business Data Cloud (BDC)** architecture — covering data extraction, transformation (via SAP Datasphere-style pipelines), KPI computation, and visualization (SAP Analytics Cloud equivalent).

---

## 🎯 Business Problem

Companies running SAP ERP face:
- Siloed procurement data across MM, FI modules
- No unified KPI framework for procurement performance
- Inability to predict delivery delays proactively
- Missed early payment discounts (working capital leakage)
- No vendor risk visibility until problems occur

## 💡 Solution

A unified P2P analytics pipeline that:
✅ Integrates 5 SAP-equivalent data sources  
✅ Computes 5 critical KPIs automatically  
✅ Scores and ranks all vendors by performance + risk  
✅ Predicts delivery delay risk for new POs  
✅ Visualizes everything in an executive Power BI dashboard  

---

## 📁 Project Structure

```
P2P_Analytics_System/
│
├── 📂 data/
│   ├── raw/                    # Original CSV datasets (SAP extracts)
│   │   ├── vendors.csv
│   │   ├── purchase_orders.csv
│   │   ├── goods_receipts.csv
│   │   ├── invoices.csv
│   │   └── payments.csv
│   ├── processed/              # Cleaned individual files
│   └── final/                  # Merged master dataset
│       └── p2p_master_dataset.csv
│
├── 📂 scripts/                 # Python processing pipeline
│   ├── 01_generate_datasets.py     # Step 1: Create all datasets
│   ├── 02_data_processing.py       # Step 2: Clean + Merge data
│   ├── 03_kpi_calculations.py      # Step 3: Compute KPIs
│   ├── 04_advanced_analytics.py    # Step 4: Risk + Trend + Prediction
│   └── 05_generate_charts.py       # Step 5: Generate charts
│
├── 📂 outputs/
│   ├── kpis/                   # KPI output files (CSV + JSON)
│   └── charts/                 # Generated chart images (PNG)
│
├── 📂 dashboard/               # Power BI files (.pbix)
├── 📂 docs/                    # Project documentation
│   └── project_report.md
└── README.md
```

---

## 📊 Datasets

| Dataset           | Rows | SAP Equivalent          | Key Columns                         |
|-------------------|------|--------------------------|--------------------------------------|
| Vendors           |  20  | Vendor Master (XK01)    | VendorID, Category, Rating           |
| Purchase Orders   | 300  | ME21N                   | POID, TotalAmount, ExpectedDelivery  |
| Goods Receipts    | 166  | MIGO (101)              | GRID, ReceivedDate, InspectionResult |
| Invoices          | 166  | MIRO                    | InvoiceID, TotalPayable, DueDate     |
| Payments          |  93  | F110                    | PaymentID, AmountPaid, DiscountTaken |

---

## 📈 KPIs Computed

| KPI                        | Result           | Business Meaning                     |
|----------------------------|------------------|---------------------------------------|
| Total Procurement Spend    | $208.3M          | Total PO spend over 2 years           |
| On-Time Delivery Rate      | 33.1%            | % of deliveries received on schedule  |
| Average Delivery Delay     | 6.5 days         | How late deliveries arrive on average |
| On-Time Payment Rate       | 24.7%            | % of invoices paid before due date    |
| Avg Procurement Cycle Time | 91.4 days        | PO creation to final payment          |
| Avg Vendor Score           | 66.1 / 100       | Composite vendor performance          |
| Discounts Missed           | $427,716         | Lost early payment discount savings   |

---

## 🔬 Advanced Analytics

### 1. 🎯 Vendor Risk Scoring
Multi-dimensional risk assessment across 5 factors (Delivery, Fulfillment, Disputes, Quality, Concentration). Outputs Risk Tiers: 🔴 High / 🟡 Medium / 🟢 Low.

### 2. 📈 Spend Trend Analysis
- Month-over-Month (MoM) growth tracking
- 3-Month rolling average smoothing
- Year-over-Year comparison
- Statistical anomaly detection (±2σ)

### 3. 🔮 Delivery Delay Prediction
Rule-based scoring model (62.7% accuracy) that classifies new POs as:
- 🔴 HIGH — Likely Delayed (11% of POs)
- 🟡 MEDIUM — Monitor Closely (73% of POs)
- 🟢 LOW — Likely On Time (16% of POs)

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python     | 3.12    | Data pipeline, analytics |
| Pandas     | Latest  | Data transformation |
| NumPy      | Latest  | Statistical calculations |
| Matplotlib | Latest  | Chart generation |
| Seaborn    | Latest  | Statistical visualizations |
| Power BI   | Desktop | Interactive dashboard |
| Git/GitHub | -       | Version control |

---

## 🚀 How to Run This Project

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn
```

### Run All Scripts in Order
```bash
# 1. Generate raw datasets
python scripts/01_generate_datasets.py

# 2. Clean and merge data
python scripts/02_data_processing.py

# 3. Calculate KPIs
python scripts/03_kpi_calculations.py

# 4. Run advanced analytics
python scripts/04_advanced_analytics.py

# 5. Generate charts
python scripts/05_generate_charts.py
```

### Power BI Dashboard
1. Open Power BI Desktop
2. Import `data/final/p2p_master_dataset.csv`
3. Import KPI files from `outputs/kpis/`
4. Follow dashboard guide in `docs/project_report.md`

---

## 💼 SAP BDC Architecture Alignment

```
Data Sources     →  Python Pipeline  →  Analytics Layer  →  Presentation
(SAP MM/FI)         (Datasphere)        (SAC Measures)       (SAC Story)
     ↕                   ↕                    ↕                   ↕
 CSV Files       →  Pandas ETL      →   KPI Engine       →  Power BI
```

---

## 📸 Dashboard Screenshots

> *[Add Power BI dashboard screenshots here after building in Power BI Desktop]*

---

## 🔮 Future Enhancements

- [ ] ML-based delay prediction (Random Forest via scikit-learn)
- [ ] Live SAP BTP OData API integration
- [ ] SAP Analytics Cloud deployment
- [ ] Streamlit web application interface
- [ ] Time-series spend forecasting (Prophet)

---

## 👤 Author

**[Your Name]**  
SAP Analytics Enthusiast | Data Engineer | BI Developer  

📧 [your.email@example.com]  
🔗 [LinkedIn Profile URL]  
🐙 [GitHub Profile URL]  

---

## 📄 License

This project is created for educational and capstone submission purposes.  
Free to use for learning. Please credit if used as reference.

---

*Built as a capstone project demonstrating SAP Business Data Cloud, procurement analytics, and end-to-end data engineering capabilities.*
