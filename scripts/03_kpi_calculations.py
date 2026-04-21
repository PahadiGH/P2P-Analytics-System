"""
SCRIPT 3: KPI Calculations
============================
This script calculates all Key Performance Indicators (KPIs)
for the Procure-to-Pay process.

KPIs are the "scorecard" of your business — like a report card.
Each KPI answers a specific business question.

SAP BDC Context:
  In SAP Analytics Cloud (SAC), these KPIs appear on "Story" dashboards.
  Here we compute them in Python and export them for Power BI.
"""

import pandas as pd
import numpy as np
import json
import os

# ─────────────────────────────────────────────────
# LOAD THE MASTER DATASET
# ─────────────────────────────────────────────────
df = pd.read_csv(
    "/home/claude/P2P_Analytics_System/data/final/p2p_master_dataset.csv",
    parse_dates=["PODate", "ExpectedDelivery", "ReceivedDate",
                 "InvoiceDate", "DueDate", "PaymentDate"]
)

KPI_PATH = "/home/claude/P2P_Analytics_System/outputs/kpis"

print("=" * 60)
print("  P2P ANALYTICS — KPI CALCULATIONS")
print("=" * 60)
print(f"  Dataset loaded: {df.shape[0]} rows × {df.shape[1]} cols\n")


# ══════════════════════════════════════════════════════════════
# KPI 1: TOTAL SPEND ANALYSIS
# Business Question: "How much are we spending, and on what?"
# Formula: Sum of all PO TotalAmount values
# ══════════════════════════════════════════════════════════════
print("📊 KPI 1: Total Spend Analysis")
print("-" * 40)

total_spend         = df["TotalAmount"].sum()
avg_po_value        = df["TotalAmount"].mean()
max_single_po       = df["TotalAmount"].max()
total_invoiced      = df["TotalPayable"].sum()
total_paid          = df["AmountPaid"].sum()
total_discounts     = df["DiscountTaken"].sum()

# Spend by Category (which type of supplier gets most money)
spend_by_category = df.groupby("Category")["TotalAmount"].sum().reset_index()
spend_by_category.columns = ["Category", "TotalSpend"]
spend_by_category["SpendPct"] = (spend_by_category["TotalSpend"] / total_spend * 100).round(2)
spend_by_category = spend_by_category.sort_values("TotalSpend", ascending=False)

# Spend by Department (which internal team buys most)
spend_by_dept = df.groupby("Department")["TotalAmount"].sum().reset_index()
spend_by_dept.columns = ["Department", "TotalSpend"]
spend_by_dept = spend_by_dept.sort_values("TotalSpend", ascending=False)

# Spend by Month (trend over time)
spend_by_month = df.groupby(["POYear", "POMonth"])["TotalAmount"].sum().reset_index()
spend_by_month.columns = ["Year", "Month", "TotalSpend"]
spend_by_month = spend_by_month.sort_values(["Year", "Month"])

print(f"  Total PO Spend:       ${total_spend:>15,.2f}")
print(f"  Total Invoiced:       ${total_invoiced:>15,.2f}")
print(f"  Total Paid:           ${total_paid:>15,.2f}")
print(f"  Total Discounts:      ${total_discounts:>15,.2f}")
print(f"  Avg PO Value:         ${avg_po_value:>15,.2f}")
print(f"  Largest Single PO:    ${max_single_po:>15,.2f}")
print(f"\n  Top 3 Spend Categories:")
for _, row in spend_by_category.head(3).iterrows():
    print(f"    • {row['Category']:<22} ${row['TotalSpend']:>12,.0f}  ({row['SpendPct']}%)")

spend_by_category.to_csv(f"{KPI_PATH}/kpi1_spend_by_category.csv", index=False)
spend_by_dept.to_csv(f"{KPI_PATH}/kpi1_spend_by_department.csv", index=False)
spend_by_month.to_csv(f"{KPI_PATH}/kpi1_spend_by_month.csv", index=False)


# ══════════════════════════════════════════════════════════════
# KPI 2: VENDOR PERFORMANCE SCORECARD
# Business Question: "Which vendors are performing well?"
# Metrics: On-time delivery %, invoice accuracy, fulfillment rate
# ══════════════════════════════════════════════════════════════
print("\n📊 KPI 2: Vendor Performance Scorecard")
print("-" * 40)

vendor_perf = df.groupby(["VendorID", "VendorName", "Category", "Rating"]).agg(
    TotalOrders        = ("POID", "count"),
    TotalSpend         = ("TotalAmount", "sum"),
    AvgDeliveryDelay   = ("DeliveryDelayDays", "mean"),
    LateDeliveries     = ("IsLateDelivery", "sum"),
    TotalDeliveries    = ("IsLateDelivery", "count"),
    AvgFulfillmentRate = ("QuantityFulfillmentRate", "mean"),
    PassedInspections  = ("InspectionResult", lambda x: (x == "Passed").sum())
).reset_index()

# Calculate On-Time Delivery Rate (%)
vendor_perf["OnTimeDeliveryRate"] = (
    (1 - vendor_perf["LateDeliveries"] / vendor_perf["TotalDeliveries"].replace(0, np.nan)) * 100
).round(2).fillna(0)

# Calculate Inspection Pass Rate (%)
vendor_perf["InspectionPassRate"] = (
    vendor_perf["PassedInspections"] / vendor_perf["TotalDeliveries"].replace(0, np.nan) * 100
).round(2).fillna(0)

# Composite Vendor Score (weighted formula):
# 40% On-Time Delivery + 30% Fulfillment Rate + 20% Inspection Pass + 10% Rating
vendor_perf["VendorScore"] = (
    vendor_perf["OnTimeDeliveryRate"]  * 0.40 +
    vendor_perf["AvgFulfillmentRate"]  * 0.30 +
    vendor_perf["InspectionPassRate"]  * 0.20 +
    vendor_perf["Rating"] / 5 * 100   * 0.10
).round(2)

# Assign Performance Tier
def assign_tier(score):
    if score >= 85:   return "A - Excellent"
    elif score >= 70: return "B - Good"
    elif score >= 55: return "C - Average"
    else:             return "D - Poor"

vendor_perf["PerformanceTier"] = vendor_perf["VendorScore"].apply(assign_tier)
vendor_perf = vendor_perf.sort_values("VendorScore", ascending=False)

print(f"  Total Vendors Evaluated: {len(vendor_perf)}")
print(f"  Avg Vendor Score:        {vendor_perf['VendorScore'].mean():.1f} / 100")
print(f"\n  Performance Tier Distribution:")
tier_counts = vendor_perf["PerformanceTier"].value_counts()
for tier, count in tier_counts.items():
    print(f"    • {tier:<20} {count} vendors")

print(f"\n  Top 3 Vendors:")
for _, row in vendor_perf.head(3).iterrows():
    print(f"    • {row['VendorName']:<30} Score: {row['VendorScore']:.1f} | {row['PerformanceTier']}")

vendor_perf.to_csv(f"{KPI_PATH}/kpi2_vendor_performance.csv", index=False)


# ══════════════════════════════════════════════════════════════
# KPI 3: DELIVERY DELAY ANALYSIS
# Business Question: "How often are deliveries late, and by how much?"
# Formula: Delivery Delay = Actual Receipt Date − Expected Delivery Date
# ══════════════════════════════════════════════════════════════
print("\n📊 KPI 3: Delivery Delay Analysis")
print("-" * 40)

# Filter rows that have GR data (deliveries only)
df_with_gr = df.dropna(subset=["ReceivedDate", "DeliveryDelayDays"])

total_deliveries    = len(df_with_gr)
late_deliveries     = (df_with_gr["DeliveryDelayDays"] > 0).sum()
on_time_deliveries  = total_deliveries - late_deliveries
avg_delay           = df_with_gr["DeliveryDelayDays"].mean()
max_delay           = df_with_gr["DeliveryDelayDays"].max()
on_time_rate        = on_time_deliveries / total_deliveries * 100

# Delay distribution: Early, On-time, Slight, Severe
def delay_category(days):
    if pd.isna(days): return "Unknown"
    if days < 0:      return "Early"
    elif days == 0:   return "On Time"
    elif days <= 7:   return "Slight Delay (1-7d)"
    elif days <= 14:  return "Moderate Delay (8-14d)"
    else:             return "Severe Delay (>14d)"

df["DelayCategory"] = df["DeliveryDelayDays"].apply(delay_category)

delay_dist = df["DelayCategory"].value_counts().reset_index()
delay_dist.columns = ["DelayCategory", "Count"]

# Average delay by vendor
delay_by_vendor = df_with_gr.groupby(["VendorName"]).agg(
    AvgDelay    = ("DeliveryDelayDays", "mean"),
    MaxDelay    = ("DeliveryDelayDays", "max"),
    TotalOrders = ("POID", "count")
).reset_index().sort_values("AvgDelay", ascending=False)

print(f"  Total Deliveries:     {total_deliveries}")
print(f"  On-Time Deliveries:   {on_time_deliveries}  ({on_time_rate:.1f}%)")
print(f"  Late Deliveries:      {late_deliveries}  ({100-on_time_rate:.1f}%)")
print(f"  Avg Delay:            {avg_delay:.1f} days")
print(f"  Max Delay:            {max_delay:.0f} days")

delay_dist.to_csv(f"{KPI_PATH}/kpi3_delay_distribution.csv", index=False)
delay_by_vendor.to_csv(f"{KPI_PATH}/kpi3_delay_by_vendor.csv", index=False)


# ══════════════════════════════════════════════════════════════
# KPI 4: PAYMENT DELAY / DPO (Days Payable Outstanding)
# Business Question: "Are we paying on time? Are we missing discounts?"
# Formula: Payment Delay = Payment Date − Invoice Due Date
# ══════════════════════════════════════════════════════════════
print("\n📊 KPI 4: Payment Delay Analysis")
print("-" * 40)

df_with_pay = df.dropna(subset=["PaymentDate", "PaymentDelayDays"])

total_payments      = len(df_with_pay)
late_payments       = (df_with_pay["PaymentDelayDays"] > 0).sum()
on_time_payments    = total_payments - late_payments
avg_payment_delay   = df_with_pay["PaymentDelayDays"].mean()
payment_on_time_pct = on_time_payments / total_payments * 100

# DPO (Days Payable Outstanding) — average days taken to pay
dpo = df_with_pay["ProcurementCycleTime"].mean()

# Early payment discounts captured
discount_captured = df["DiscountTaken"].sum()
discount_missed   = df[
    (df["PaymentTerms"] == "2/10NET30") & (df["DiscountTaken"] == 0)
]["TotalPayable"].sum() * 0.02

payment_perf = df_with_pay.groupby("VendorName").agg(
    TotalInvoices     = ("InvoiceID", "count"),
    AvgPaymentDelay   = ("PaymentDelayDays", "mean"),
    LatePayments      = ("IsLatePayment", "sum"),
    TotalAmountPaid   = ("AmountPaid", "sum")
).reset_index()
payment_perf["OnTimePaymentRate"] = (
    (1 - payment_perf["LatePayments"] / payment_perf["TotalInvoices"]) * 100
).round(2)

print(f"  Total Payments:       {total_payments}")
print(f"  On-Time Payments:     {on_time_payments}  ({payment_on_time_pct:.1f}%)")
print(f"  Late Payments:        {late_payments}")
print(f"  Avg Payment Delay:    {avg_payment_delay:.1f} days")
print(f"  DPO (Avg Cycle):      {dpo:.1f} days")
print(f"  Discounts Captured:   ${discount_captured:,.2f}")
print(f"  Discounts Missed:     ${discount_missed:,.2f}")

payment_perf.to_csv(f"{KPI_PATH}/kpi4_payment_analysis.csv", index=False)


# ══════════════════════════════════════════════════════════════
# KPI 5: PROCUREMENT CYCLE TIME
# Business Question: "How long does it take from PO to Payment?"
# Formula: ProcurementCycleTime = PaymentDate − PODate
# ══════════════════════════════════════════════════════════════
print("\n📊 KPI 5: Procurement Cycle Time")
print("-" * 40)

df_with_cycle = df.dropna(subset=["ProcurementCycleTime"])

avg_cycle   = df_with_cycle["ProcurementCycleTime"].mean()
median_cycle= df_with_cycle["ProcurementCycleTime"].median()
max_cycle   = df_with_cycle["ProcurementCycleTime"].max()
min_cycle   = df_with_cycle["ProcurementCycleTime"].min()

# Break cycle time by stage (approximate)
avg_delivery_time = (df["ReceivedDate"] - df["PODate"]).dt.days.mean()
avg_invoice_time  = (df["InvoiceDate"] - df["ReceivedDate"]).dt.days.mean()
avg_payment_time  = (df["PaymentDate"] - df["DueDate"]).dt.days.mean()

# Cycle time by vendor category
cycle_by_category = df_with_cycle.groupby("Category")["ProcurementCycleTime"].agg(
    ["mean", "median", "min", "max", "count"]
).reset_index()
cycle_by_category.columns = ["Category", "AvgDays", "MedianDays", "MinDays", "MaxDays", "Count"]
cycle_by_category = cycle_by_category.sort_values("AvgDays", ascending=False)

print(f"  Avg Procurement Cycle:    {avg_cycle:.1f} days")
print(f"  Median Cycle Time:        {median_cycle:.1f} days")
print(f"  Fastest Cycle:            {min_cycle:.0f} days")
print(f"  Slowest Cycle:            {max_cycle:.0f} days")
print(f"\n  Avg Time by Stage:")
print(f"    PO → GR (Delivery):     {avg_delivery_time:.1f} days")
print(f"    GR → Invoice:           {avg_invoice_time:.1f} days")
print(f"    Invoice → Payment:      {avg_payment_time:.1f} days")

cycle_by_category.to_csv(f"{KPI_PATH}/kpi5_cycle_time_by_category.csv", index=False)


# ══════════════════════════════════════════════════════════════
# SAVE CONSOLIDATED KPI SUMMARY (for dashboard cards)
# ══════════════════════════════════════════════════════════════
kpi_summary = {
    "TotalSpendUSD":          round(total_spend, 2),
    "TotalInvoicedUSD":       round(total_invoiced, 2),
    "TotalPaidUSD":           round(total_paid, 2),
    "DiscountsCapturedUSD":   round(discount_captured, 2),
    "AvgPOValueUSD":          round(avg_po_value, 2),
    "TotalVendors":           len(vendor_perf),
    "AvgVendorScore":         round(vendor_perf["VendorScore"].mean(), 2),
    "OnTimeDeliveryRate_Pct": round(on_time_rate, 2),
    "AvgDeliveryDelay_Days":  round(avg_delay, 2),
    "OnTimePaymentRate_Pct":  round(payment_on_time_pct, 2),
    "AvgPaymentDelay_Days":   round(avg_payment_delay, 2),
    "AvgCycleTime_Days":      round(avg_cycle, 2),
    "DPO_Days":               round(dpo, 2)
}

# Save as CSV (for Power BI)
kpi_df = pd.DataFrame([kpi_summary]).T.reset_index()
kpi_df.columns = ["KPI_Name", "KPI_Value"]
kpi_df.to_csv(f"{KPI_PATH}/kpi_summary_card.csv", index=False)

# Save as JSON (for documentation)
with open(f"{KPI_PATH}/kpi_summary.json", "w") as f:
    json.dump(kpi_summary, f, indent=2)

print("\n" + "=" * 60)
print("✅  ALL KPIs CALCULATED & SAVED!")
print("=" * 60)
print(f"\n📂 Files saved to: {KPI_PATH}/")
for f in os.listdir(KPI_PATH):
    print(f"   • {f}")
