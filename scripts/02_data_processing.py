"""
SCRIPT 2: Data Cleaning & Processing
======================================
This script reads the raw CSV files, cleans them, merges them together,
and creates one final "master" dataset ready for analysis.

Think of it like this:
  Raw Data → Clean Data → Merged Data → Final Analysis-Ready Data

SAP BDC Context:
  In SAP Business Data Cloud, this step is like running a "Data Flow"
  in SAP Datasphere where tables are joined via star schema logic.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore")   # Suppress non-critical warnings

# ─────────────────────────────────────────────────
# PATHS — where to read from and write to
# ─────────────────────────────────────────────────
RAW_PATH       = "/home/claude/P2P_Analytics_System/data/raw"
PROCESSED_PATH = "/home/claude/P2P_Analytics_System/data/processed"
FINAL_PATH     = "/home/claude/P2P_Analytics_System/data/final"

print("=" * 60)
print("  P2P ANALYTICS — DATA CLEANING & PROCESSING")
print("=" * 60)

# ─────────────────────────────────────────────────────────────────
# STEP 2.1 — LOAD ALL RAW CSV FILES
# Think of this as "opening" all the Excel files at once
# ─────────────────────────────────────────────────────────────────
print("\n📂 STEP 1: Loading raw datasets...")

df_vendors  = pd.read_csv(f"{RAW_PATH}/vendors.csv")
df_po       = pd.read_csv(f"{RAW_PATH}/purchase_orders.csv")
df_gr       = pd.read_csv(f"{RAW_PATH}/goods_receipts.csv")
df_invoices = pd.read_csv(f"{RAW_PATH}/invoices.csv")
df_payments = pd.read_csv(f"{RAW_PATH}/payments.csv")

print(f"  ✅ vendors.csv        → {df_vendors.shape[0]} rows, {df_vendors.shape[1]} cols")
print(f"  ✅ purchase_orders.csv → {df_po.shape[0]} rows, {df_po.shape[1]} cols")
print(f"  ✅ goods_receipts.csv  → {df_gr.shape[0]} rows, {df_gr.shape[1]} cols")
print(f"  ✅ invoices.csv        → {df_invoices.shape[0]} rows, {df_invoices.shape[1]} cols")
print(f"  ✅ payments.csv        → {df_payments.shape[0]} rows, {df_payments.shape[1]} cols")


# ─────────────────────────────────────────────────────────────────
# STEP 2.2 — CLEAN EACH DATASET
# Cleaning = fixing data types, removing bad rows, filling blanks
# ─────────────────────────────────────────────────────────────────
print("\n🧹 STEP 2: Cleaning datasets...")

# ── Identify which columns contain dates in each table ──
date_cols = {
    "vendors":         ["OnboardingDate"],
    "purchase_orders": ["PODate", "ExpectedDelivery"],
    "goods_receipts":  ["ReceivedDate", "ExpectedDate"],
    "invoices":        ["InvoiceDate", "DueDate"],
    "payments":        ["PaymentDate", "DueDate"]
}

def clean_dataframe(df, name, date_columns):
    """
    Cleans a single dataframe:
    1. Converts date columns from text → proper date format
    2. Removes completely duplicate rows
    3. Strips extra spaces from text columns
    4. Fills missing number columns with 0
    """
    print(f"\n  🔧 Cleaning: {name}")

    # Step A: Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"     Duplicates removed: {before - after}")

    # Step B: Convert date columns from string to datetime
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            # errors="coerce" means: if a date is invalid, replace it with NaT (blank date)

    # Step C: Strip extra whitespace from text columns
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # Step D: Fill missing numeric values with 0
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[num_cols] = df[num_cols].fillna(0)

    # Step E: Fill missing text with "Unknown"
    df[text_cols] = df[text_cols].fillna("Unknown")

    # Step F: Count and report any remaining NaT date values
    for col in date_columns:
        if col in df.columns:
            bad_dates = df[col].isna().sum()
            if bad_dates > 0:
                print(f"     ⚠️  {col}: {bad_dates} invalid dates found (marked as NaT)")

    print(f"     ✅ Clean shape: {df.shape[0]} rows × {df.shape[1]} cols")
    return df

df_vendors  = clean_dataframe(df_vendors,  "vendors",         date_cols["vendors"])
df_po       = clean_dataframe(df_po,       "purchase_orders", date_cols["purchase_orders"])
df_gr       = clean_dataframe(df_gr,       "goods_receipts",  date_cols["goods_receipts"])
df_invoices = clean_dataframe(df_invoices, "invoices",        date_cols["invoices"])
df_payments = clean_dataframe(df_payments, "payments",        date_cols["payments"])

# ── Save cleaned datasets ──
df_vendors.to_csv(f"{PROCESSED_PATH}/vendors_clean.csv", index=False)
df_po.to_csv(f"{PROCESSED_PATH}/purchase_orders_clean.csv", index=False)
df_gr.to_csv(f"{PROCESSED_PATH}/goods_receipts_clean.csv", index=False)
df_invoices.to_csv(f"{PROCESSED_PATH}/invoices_clean.csv", index=False)
df_payments.to_csv(f"{PROCESSED_PATH}/payments_clean.csv", index=False)
print("\n  💾 Cleaned files saved to /data/processed/")


# ─────────────────────────────────────────────────────────────────
# STEP 2.3 — MERGE DATASETS INTO ONE MASTER TABLE
# Like doing VLOOKUP in Excel or JOIN in SQL
#
# Merge Chain:
#   PO → GR → Invoice → Payment → Vendor
#
# This is the "star schema" concept from SAP BDC / Datasphere
# ─────────────────────────────────────────────────────────────────
print("\n🔗 STEP 3: Merging all datasets...")

# Merge 1: Join Purchase Orders + Vendors (on VendorID)
# LEFT JOIN = keep all PO rows even if no matching vendor
df_merged = pd.merge(
    df_po,           # Left table: Purchase Orders
    df_vendors,      # Right table: Vendors
    on="VendorID",   # The common column between them
    how="left",      # Left join: keep all rows from df_po
    suffixes=("_PO", "_Vendor")  # Add suffix if columns have same name
)
print(f"  Step 3.1 — PO + Vendors:      {df_merged.shape[0]} rows")

# Merge 2: Add Goods Receipts
df_merged = pd.merge(
    df_merged,
    df_gr[["POID", "GRID", "ReceivedDate", "ReceivedQuantity", "OrderedQuantity",
           "InspectionResult", "GRStatus"]],
    on="POID",
    how="left"
)
print(f"  Step 3.2 — + Goods Receipts:  {df_merged.shape[0]} rows")

# Merge 3: Add Invoices
df_merged = pd.merge(
    df_merged,
    df_invoices[["POID", "InvoiceID", "InvoiceDate", "InvoiceAmount",
                 "TaxAmount", "TotalPayable", "InvoiceStatus", "DueDate"]],
    on="POID",
    how="left"
)
print(f"  Step 3.3 — + Invoices:        {df_merged.shape[0]} rows")

# Merge 4: Add Payments (join on InvoiceID)
df_merged = pd.merge(
    df_merged,
    df_payments[["InvoiceID", "PaymentID", "PaymentDate", "AmountPaid",
                 "DiscountTaken", "PaymentMethod", "PaymentStatus"]],
    on="InvoiceID",
    how="left"
)
print(f"  Step 3.4 — + Payments:        {df_merged.shape[0]} rows")
print(f"  Final merged table: {df_merged.shape[0]} rows × {df_merged.shape[1]} columns")


# ─────────────────────────────────────────────────────────────────
# STEP 2.4 — CALCULATE DERIVED COLUMNS (KPI prep)
# These are new columns we calculate from existing date columns
# ─────────────────────────────────────────────────────────────────
print("\n📐 STEP 4: Creating calculated / derived columns...")

# Column 1: DeliveryDelayDays
# How many days late (or early) was the delivery?
# Positive = late, Negative = early
df_merged["DeliveryDelayDays"] = (
    df_merged["ReceivedDate"] - df_merged["ExpectedDelivery"]
).dt.days
print("  ✅ DeliveryDelayDays — Actual delivery minus expected delivery")

# Column 2: PaymentDelayDays
# How many days after due date did we pay?
df_merged["PaymentDelayDays"] = (
    df_merged["PaymentDate"] - df_merged["DueDate"]
).dt.days
print("  ✅ PaymentDelayDays — Payment date minus invoice due date")

# Column 3: ProcurementCycleTime
# Total days from PO creation to actual payment
df_merged["ProcurementCycleTime"] = (
    df_merged["PaymentDate"] - df_merged["PODate"]
).dt.days
print("  ✅ ProcurementCycleTime — PO date to payment date (end-to-end)")

# Column 4: QuantityFulfillmentRate
# What % of the ordered quantity was actually received?
df_merged["QuantityFulfillmentRate"] = (
    df_merged["ReceivedQuantity"] / df_merged["Quantity"] * 100
).round(2)
print("  ✅ QuantityFulfillmentRate — Received qty ÷ Ordered qty × 100")

# Column 5: IsLateDelivery
# Binary flag: 1 = late delivery, 0 = on time or early
df_merged["IsLateDelivery"] = (df_merged["DeliveryDelayDays"] > 0).astype(int)
print("  ✅ IsLateDelivery — 1 if late, 0 if on time")

# Column 6: IsLatePayment
# Binary flag: 1 = we paid after due date
df_merged["IsLatePayment"] = (df_merged["PaymentDelayDays"] > 0).astype(int)
print("  ✅ IsLatePayment — 1 if paid late, 0 if on time")

# Column 7: PO Year and Month (for time-series analysis)
df_merged["POYear"]  = df_merged["PODate"].dt.year
df_merged["POMonth"] = df_merged["PODate"].dt.month
df_merged["POMonthName"] = df_merged["PODate"].dt.strftime("%b")  # e.g., "Jan", "Feb"
print("  ✅ POYear, POMonth, POMonthName — For time-based charts")

# Column 8: SpendBand — categorize spend amount
def categorize_spend(amount):
    if amount < 5000:
        return "Small (<5K)"
    elif amount < 50000:
        return "Medium (5K–50K)"
    elif amount < 200000:
        return "Large (50K–200K)"
    else:
        return "Strategic (>200K)"

df_merged["SpendBand"] = df_merged["TotalAmount"].apply(categorize_spend)
print("  ✅ SpendBand — Categorizes PO by spend size")


# ─────────────────────────────────────────────────────────────────
# STEP 2.5 — FINAL CLEANUP & COLUMN RENAMING
# ─────────────────────────────────────────────────────────────────
print("\n🔁 STEP 5: Final cleanup...")

# Remove columns we no longer need (avoid confusion)
cols_to_drop = ["ContactEmail", "BankAccount"]
df_final = df_merged.drop(columns=[c for c in cols_to_drop if c in df_merged.columns])

# Keep only rows that have at minimum a valid PO date
df_final = df_final.dropna(subset=["PODate"])

# Reset the index so row numbers are clean (0, 1, 2...)
df_final = df_final.reset_index(drop=True)

print(f"  ✅ Final dataset: {df_final.shape[0]} rows × {df_final.shape[1]} columns")

# ─────────────────────────────────────────────────────────────────
# STEP 2.6 — SAVE FINAL MASTER DATASET
# ─────────────────────────────────────────────────────────────────
final_file = f"{FINAL_PATH}/p2p_master_dataset.csv"
df_final.to_csv(final_file, index=False)

print(f"\n💾 Final master dataset saved: {final_file}")
print("\n" + "=" * 60)
print("  ALL COLUMNS IN FINAL DATASET:")
print("=" * 60)
for i, col in enumerate(df_final.columns, 1):
    dtype = str(df_final[col].dtype)
    print(f"  {i:>2}. {col:<35} [{dtype}]")

print("\n" + "=" * 60)
print("✅  DATA PROCESSING COMPLETE!")
print("=" * 60)
print(f"\nTotal Spend in Dataset:  ${df_final['TotalAmount'].sum():,.2f}")
print(f"Avg Delivery Delay:       {df_final['DeliveryDelayDays'].mean():.1f} days")
print(f"Late Delivery Rate:       {df_final['IsLateDelivery'].mean()*100:.1f}%")
print(f"Late Payment Rate:        {df_final['IsLatePayment'].mean()*100:.1f}%")
