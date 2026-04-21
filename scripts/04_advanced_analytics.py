"""
SCRIPT 4: Advanced Analytics
==============================
This script adds 3 advanced analytical features:
  1. Vendor Risk Scoring     — classify vendors by risk level
  2. Spend Trend Analysis    — detect if spending is going up/down
  3. Delay Prediction        — predict if a future PO might be late

These features make the project stand out and show real analytical thinking.

SAP Context:
  These analyses map to SAP Analytics Cloud (SAC) Predictive Planning,
  and SAP BTP Data Intelligence pipelines.
"""

import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────
df = pd.read_csv(
    "/home/claude/P2P_Analytics_System/data/final/p2p_master_dataset.csv",
    parse_dates=["PODate", "ExpectedDelivery", "ReceivedDate",
                 "InvoiceDate", "DueDate", "PaymentDate"]
)

ADVANCED_PATH = "/home/claude/P2P_Analytics_System/outputs"

print("=" * 65)
print("  P2P ANALYTICS — ADVANCED ANALYTICS MODULE")
print("=" * 65)


# ══════════════════════════════════════════════════════════════════
# ADVANCED MODULE 1: VENDOR RISK SCORING
#
# Business Purpose:
#   Identify vendors that pose financial or operational risk.
#   Risk = combination of late delivery, late payment, inspection
#          failures, low fulfillment, and invoice disputes.
#
# Logic:
#   We score each vendor across 5 risk dimensions (0-20 points each)
#   and combine into a Risk Score (0-100, where 100 = VERY RISKY).
# ══════════════════════════════════════════════════════════════════
print("\n🎯 MODULE 1: VENDOR RISK SCORING")
print("-" * 45)

vendor_risk = df.groupby(["VendorID", "VendorName", "Category", "Country"]).agg(
    TotalOrders           = ("POID",                 "count"),
    TotalSpend            = ("TotalAmount",           "sum"),
    AvgDeliveryDelay      = ("DeliveryDelayDays",     "mean"),
    LateDeliveryCount     = ("IsLateDelivery",        "sum"),
    TotalDeliveries       = ("IsLateDelivery",        "count"),
    AvgFulfillmentRate    = ("QuantityFulfillmentRate","mean"),
    DisputedInvoices      = ("InvoiceStatus",         lambda x: (x == "Disputed").sum()),
    FailedInspections     = ("InspectionResult",      lambda x: (x == "Failed").sum()),
    LatePaymentCount      = ("IsLatePayment",         "sum"),
    TotalPayments         = ("IsLatePayment",         "count"),
    AvgCycleTime          = ("ProcurementCycleTime",  "mean")
).reset_index()

# ── RISK DIMENSION 1: Late Delivery Risk (0-20 points) ──
# Higher late delivery % = higher risk
vendor_risk["LateDeliveryRate"] = (
    vendor_risk["LateDeliveryCount"] / vendor_risk["TotalDeliveries"].replace(0, np.nan)
).fillna(0)
vendor_risk["Risk_Delivery"] = (vendor_risk["LateDeliveryRate"] * 20).round(2)

# ── RISK DIMENSION 2: Fulfillment Risk (0-20 points) ──
# Low fulfillment rate = higher risk (inverted: 100% fulfillment = 0 risk)
vendor_risk["Risk_Fulfillment"] = (
    (1 - vendor_risk["AvgFulfillmentRate"] / 100) * 20
).round(2)

# ── RISK DIMENSION 3: Invoice Dispute Risk (0-20 points) ──
# More disputed invoices = higher risk
vendor_risk["DisputeRate"] = (
    vendor_risk["DisputedInvoices"] / vendor_risk["TotalOrders"].replace(0, np.nan)
).fillna(0)
vendor_risk["Risk_Dispute"] = (vendor_risk["DisputeRate"] * 20).round(2)

# ── RISK DIMENSION 4: Quality Risk (0-20 points) ──
# More failed inspections = higher risk
vendor_risk["FailureRate"] = (
    vendor_risk["FailedInspections"] / vendor_risk["TotalDeliveries"].replace(0, np.nan)
).fillna(0)
vendor_risk["Risk_Quality"] = (vendor_risk["FailureRate"] * 20).round(2)

# ── RISK DIMENSION 5: Spend Concentration Risk (0-20 points) ──
# Very high spend on one vendor = concentration risk (over-dependence)
total_spend = vendor_risk["TotalSpend"].sum()
vendor_risk["SpendSharePct"] = (vendor_risk["TotalSpend"] / total_spend * 100)
vendor_risk["Risk_Concentration"] = (vendor_risk["SpendSharePct"] / 100 * 20).round(2)

# ── COMPOSITE RISK SCORE (weighted) ──
vendor_risk["TotalRiskScore"] = (
    vendor_risk["Risk_Delivery"]      * 0.30 +   # 30% weight
    vendor_risk["Risk_Fulfillment"]   * 0.20 +   # 20% weight
    vendor_risk["Risk_Dispute"]       * 0.20 +   # 20% weight
    vendor_risk["Risk_Quality"]       * 0.20 +   # 20% weight
    vendor_risk["Risk_Concentration"] * 0.10      # 10% weight
).round(2)

# ── RISK TIER ──
def assign_risk_tier(score):
    if score >= 12:   return "🔴 HIGH RISK"
    elif score >= 7:  return "🟡 MEDIUM RISK"
    else:             return "🟢 LOW RISK"

vendor_risk["RiskTier"] = vendor_risk["TotalRiskScore"].apply(assign_risk_tier)
vendor_risk = vendor_risk.sort_values("TotalRiskScore", ascending=False)

print("  Vendor Risk Tier Summary:")
for tier in ["🔴 HIGH RISK", "🟡 MEDIUM RISK", "🟢 LOW RISK"]:
    count = (vendor_risk["RiskTier"] == tier).sum()
    print(f"    {tier:<20} : {count} vendors")

print(f"\n  Top 5 Riskiest Vendors:")
print(f"  {'Vendor':<30} {'Score':>6}  {'Tier'}")
print(f"  {'-'*55}")
for _, row in vendor_risk.head(5).iterrows():
    print(f"  {row['VendorName']:<30} {row['TotalRiskScore']:>6.1f}  {row['RiskTier']}")

vendor_risk.to_csv(f"{ADVANCED_PATH}/kpis/vendor_risk_scores.csv", index=False)
print(f"\n  ✅ Saved: vendor_risk_scores.csv")


# ══════════════════════════════════════════════════════════════════
# ADVANCED MODULE 2: SPEND TREND ANALYSIS
#
# Business Purpose:
#   Track how spending is changing month over month.
#   Identify which categories/vendors are growing vs shrinking.
#   Detect anomalies (unusual spikes or drops).
#
# Logic:
#   Calculate Month-over-Month (MoM) growth rate.
#   Use rolling average to smooth the trend line.
#   Flag months where spend is >2 standard deviations from mean.
# ══════════════════════════════════════════════════════════════════
print("\n📈 MODULE 2: SPEND TREND ANALYSIS")
print("-" * 45)

# Monthly spend totals
monthly_spend = df.groupby(["POYear", "POMonth"]).agg(
    TotalSpend  = ("TotalAmount", "sum"),
    OrderCount  = ("POID",        "count"),
    AvgPOValue  = ("TotalAmount", "mean"),
    UniqueVendors = ("VendorID",  "nunique")
).reset_index()

monthly_spend["YearMonth"] = pd.to_datetime(
    monthly_spend[["POYear", "POMonth"]].rename(
        columns={"POYear": "year", "POMonth": "month"}
    ).assign(day=1)
)
monthly_spend = monthly_spend.sort_values("YearMonth")

# Month-over-Month Growth Rate (%)
monthly_spend["MoMGrowth_Pct"] = (
    monthly_spend["TotalSpend"].pct_change() * 100
).round(2)

# 3-Month Rolling Average (smooths out noise)
monthly_spend["Rolling3MonthAvg"] = (
    monthly_spend["TotalSpend"].rolling(window=3, min_periods=1).mean()
).round(2)

# Year-over-Year comparison (current month vs same month last year)
monthly_spend["SpendLastYear"] = monthly_spend["TotalSpend"].shift(12)
monthly_spend["YoYGrowth_Pct"] = (
    (monthly_spend["TotalSpend"] - monthly_spend["SpendLastYear"])
    / monthly_spend["SpendLastYear"] * 100
).round(2)

# Anomaly Detection: flag months with spend > 2 std deviations from mean
mean_spend = monthly_spend["TotalSpend"].mean()
std_spend  = monthly_spend["TotalSpend"].std()
monthly_spend["IsAnomaly"]     = (
    (monthly_spend["TotalSpend"] > mean_spend + 2 * std_spend) |
    (monthly_spend["TotalSpend"] < mean_spend - 2 * std_spend)
)
monthly_spend["AnomalyLabel"]  = monthly_spend["IsAnomaly"].map(
    {True: "⚠️ Anomaly", False: "Normal"}
)

# Category-wise trend
category_trend = df.groupby(["POYear", "POMonth", "Category"])["TotalAmount"].sum().reset_index()
category_trend.columns = ["Year", "Month", "Category", "TotalSpend"]
category_trend = category_trend.sort_values(["Year", "Month"])

# Trend direction summary
if monthly_spend["MoMGrowth_Pct"].iloc[-3:].mean() > 0:
    trend_direction = "📈 INCREASING"
else:
    trend_direction = "📉 DECREASING"

anomalies_found = monthly_spend["IsAnomaly"].sum()
peak_month = monthly_spend.loc[monthly_spend["TotalSpend"].idxmax(), "YearMonth"]

print(f"  Overall Spend Trend:      {trend_direction}")
print(f"  Peak Spend Month:         {peak_month.strftime('%B %Y')}")
print(f"  Anomalous Months Found:   {anomalies_found}")
print(f"  Avg Monthly Spend:        ${mean_spend:,.0f}")
print(f"  Last Month MoM Growth:    {monthly_spend['MoMGrowth_Pct'].iloc[-1]:+.1f}%")

monthly_spend["YearMonth"] = monthly_spend["YearMonth"].astype(str)
monthly_spend.to_csv(f"{ADVANCED_PATH}/kpis/spend_trend_analysis.csv", index=False)
category_trend.to_csv(f"{ADVANCED_PATH}/kpis/category_spend_trend.csv", index=False)
print(f"\n  ✅ Saved: spend_trend_analysis.csv, category_spend_trend.csv")


# ══════════════════════════════════════════════════════════════════
# ADVANCED MODULE 3: DELIVERY DELAY PREDICTION (Rule-Based Model)
#
# Business Purpose:
#   Predict whether a new Purchase Order is likely to be delayed.
#   This helps the procurement team take proactive action.
#
# Logic (Rule-Based — no ML library needed):
#   We create a "Delay Risk Score" for each PO based on:
#   1. Vendor's historical late delivery rate
#   2. Lead time (days from PO to expected delivery)
#   3. Ordered quantity (very large orders risk delays)
#   4. Vendor category's average delay
#   5. Specific plant performance
#
#   The score is then used to classify: Low / Medium / High delay risk.
# ══════════════════════════════════════════════════════════════════
print("\n🔮 MODULE 3: DELIVERY DELAY PREDICTION (Rule-Based)")
print("-" * 45)

# ── Build risk profile from historical data ──

# A: Vendor late delivery rate
vendor_late_rate = df.groupby("VendorID").agg(
    VendorLateRate   = ("IsLateDelivery", "mean"),
    VendorAvgDelay   = ("DeliveryDelayDays", "mean")
).reset_index()

# B: Category average delay
category_avg_delay = df.groupby("Category").agg(
    CategoryAvgDelay = ("DeliveryDelayDays", "mean")
).reset_index()

# C: Plant performance
plant_avg_delay = df.groupby("PlantCode").agg(
    PlantAvgDelay = ("DeliveryDelayDays", "mean")
).reset_index()

# Merge profiles back into main data
df_pred = df.merge(vendor_late_rate, on="VendorID", how="left")
df_pred = df_pred.merge(category_avg_delay, on="Category", how="left")
df_pred = df_pred.merge(plant_avg_delay, on="PlantCode", how="left")

# Lead time = Expected Delivery Date - PO Date
df_pred["LeadTimeDays"] = (df_pred["ExpectedDelivery"] - df_pred["PODate"]).dt.days

# ── DELAY RISK SCORE CALCULATION (0-100) ──

# Factor 1: Vendor's historical late delivery rate (0-40 pts)
df_pred["F1_VendorRisk"] = (df_pred["VendorLateRate"].fillna(0.5) * 40).round(2)

# Factor 2: Lead Time Risk — very short or very long lead times are risky (0-25 pts)
# Short lead time = not enough time for supplier; Very long = more uncertainty
def lead_time_risk(days):
    if pd.isna(days) or days <= 0:  return 25    # No lead time = max risk
    elif days < 7:                   return 20    # Very short
    elif days <= 21:                 return 5     # Reasonable
    elif days <= 45:                 return 10    # Normal
    else:                            return 18    # Very long = uncertainty

df_pred["F2_LeadTimeRisk"] = df_pred["LeadTimeDays"].apply(lead_time_risk)

# Factor 3: Order Quantity Risk — very large orders are harder to fulfill on time (0-20 pts)
qty_max = df_pred["Quantity"].max()
df_pred["F3_QuantityRisk"] = (df_pred["Quantity"] / qty_max * 20).round(2)

# Factor 4: Category historical delay risk (0-15 pts)
cat_delay_max = category_avg_delay["CategoryAvgDelay"].max()
df_pred["F4_CategoryRisk"] = (
    df_pred["CategoryAvgDelay"].fillna(0) / cat_delay_max * 15
).round(2)

# ── COMPOSITE DELAY RISK SCORE ──
df_pred["DelayRiskScore"] = (
    df_pred["F1_VendorRisk"]   +
    df_pred["F2_LeadTimeRisk"] +
    df_pred["F3_QuantityRisk"] +
    df_pred["F4_CategoryRisk"]
).round(2)

# ── CLASSIFY RISK LEVEL ──
def classify_delay_risk(score):
    if score >= 55:   return "🔴 HIGH — Likely Delayed"
    elif score >= 35: return "🟡 MEDIUM — Monitor Closely"
    else:             return "🟢 LOW — Likely On Time"

df_pred["DelayRiskLevel"] = df_pred["DelayRiskScore"].apply(classify_delay_risk)

# Validate: compare prediction vs actual (for rows where we have actual data)
df_pred_valid = df_pred.dropna(subset=["DeliveryDelayDays"])
df_pred_valid["PredictedLate"] = (df_pred_valid["DelayRiskScore"] >= 35).astype(int)
df_pred_valid["ActualLate"]    = (df_pred_valid["DeliveryDelayDays"] > 0).astype(int)
df_pred_valid["CorrectPrediction"] = (
    df_pred_valid["PredictedLate"] == df_pred_valid["ActualLate"]
)

accuracy = df_pred_valid["CorrectPrediction"].mean() * 100
print(f"  Rule-Based Model Accuracy:  {accuracy:.1f}%")

# Risk level distribution
print(f"\n  Delay Risk Distribution:")
for level in ["🔴 HIGH — Likely Delayed", "🟡 MEDIUM — Monitor Closely", "🟢 LOW — Likely On Time"]:
    count = (df_pred["DelayRiskLevel"] == level).sum()
    pct   = count / len(df_pred) * 100
    print(f"    {level:<35} {count:>4} POs  ({pct:.1f}%)")

# Save prediction dataset
prediction_output = df_pred[[
    "POID", "VendorID", "VendorName", "Category", "Material",
    "LeadTimeDays", "Quantity", "TotalAmount",
    "F1_VendorRisk", "F2_LeadTimeRisk", "F3_QuantityRisk", "F4_CategoryRisk",
    "DelayRiskScore", "DelayRiskLevel",
    "DeliveryDelayDays", "IsLateDelivery"
]]
prediction_output.to_csv(f"{ADVANCED_PATH}/kpis/delay_risk_predictions.csv", index=False)
print(f"\n  ✅ Saved: delay_risk_predictions.csv")

print("\n" + "=" * 65)
print("✅  ALL ADVANCED ANALYTICS COMPLETE!")
print("=" * 65)
