"""
SCRIPT 1: Dataset Generation
==============================
This script creates all 5 datasets needed for the P2P Analytics project.
Think of this like creating Excel sheets with realistic business data.

SAP Context:
- Vendors       = Supplier master data (like SAP MM Vendor Master)
- Purchase Orders = Buying requests (like SAP ME21N)
- Goods Receipts  = Confirmation goods arrived (like SAP MIGO)
- Invoices       = Supplier bills (like SAP MIRO)
- Payments       = Money sent to suppliers (like SAP F110)
"""

import pandas as pd          # For creating and managing tables (like Excel in Python)
import numpy as np           # For math operations and random numbers
import random                # For generating random choices
from datetime import datetime, timedelta  # For working with dates
import os                    # For file/folder operations

# ─────────────────────────────────────────────────
# SET RANDOM SEED (so your data stays consistent)
# ─────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────────
# HELPER FUNCTION: Generate a random date
# ─────────────────────────────────────────────────
def random_date(start_date, end_date):
    """Returns a random date between start_date and end_date"""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Define date range for our data (2 years of business data)
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 31)

# ─────────────────────────────────────────────────────────────────────
# DATASET 1: VENDORS
# Purpose: Master list of all suppliers our company buys from.
# SAP Equivalent: Vendor Master (Transaction XK01/XK03)
# ─────────────────────────────────────────────────────────────────────
print("📦 Creating Vendors dataset...")

vendor_names = [
    "Alpha Tech Supplies", "BetaCore Industries", "Gamma Solutions Ltd",
    "Delta Manufacturing", "Epsilon Electronics", "Zeta Raw Materials",
    "Eta Global Traders", "Theta Packaging Co", "Iota Steel Works",
    "Kappa Office Supplies", "Lambda Logistics", "Mu Chemical Corp",
    "Nu Paper Mills", "Xi Furniture Works", "Omicron IT Services",
    "Pi Hardware Ltd", "Rho Consulting Group", "Sigma Plastics Co",
    "Tau Energy Systems", "Upsilon AutoParts"
]

countries = ["India", "USA", "Germany", "UK", "China", "Japan", "UAE", "Singapore", "France", "Australia"]
categories = ["Electronics", "Raw Materials", "Office Supplies", "IT Services", "Logistics",
               "Manufacturing", "Chemicals", "Packaging", "Hardware", "Consulting"]
payment_terms = ["NET30", "NET45", "NET60", "NET15", "2/10NET30"]

vendors = []
for i, name in enumerate(vendor_names):
    vendor = {
        "VendorID":       f"V{str(i+1).zfill(4)}",     # e.g., V0001, V0002
        "VendorName":     name,
        "Country":        random.choice(countries),
        "Category":       categories[i % len(categories)],
        "PaymentTerms":   random.choice(payment_terms),
        "Rating":         round(random.uniform(2.5, 5.0), 1),   # Vendor rating out of 5
        "IsActive":       random.choice(["Yes", "Yes", "Yes", "No"]),  # 75% active
        "ContactEmail":   f"contact@{name.lower().replace(' ', '')}.com",
        "CreditLimit":    random.choice([50000, 100000, 200000, 500000, 1000000]),
        "OnboardingDate": random_date(datetime(2018, 1, 1), datetime(2022, 12, 31)).strftime("%Y-%m-%d")
    }
    vendors.append(vendor)

df_vendors = pd.DataFrame(vendors)

# ─────────────────────────────────────────────────────────────────────
# DATASET 2: PURCHASE ORDERS (PO)
# Purpose: Records of what we ordered, from whom, and at what price.
# SAP Equivalent: Purchase Order (Transaction ME21N/ME23N)
# ─────────────────────────────────────────────────────────────────────
print("📋 Creating Purchase Orders dataset...")

materials = [
    "Laptop", "Office Chair", "Steel Rod", "Printer", "Ethernet Cable",
    "Server Rack", "A4 Paper Ream", "Chemical Solvent", "Plastic Mold",
    "Electric Motor", "Safety Gloves", "Network Switch", "Industrial Fan",
    "Packaging Box", "Consulting Hours", "Software License", "Diesel Generator",
    "Aluminium Sheet", "Conveyor Belt", "Fire Extinguisher"
]

departments = ["IT", "Operations", "Finance", "HR", "Procurement", "Manufacturing", "Admin", "Logistics"]

purchase_orders = []
vendor_ids = [v["VendorID"] for v in vendors]

for i in range(300):  # 300 Purchase Orders
    po_date = random_date(START_DATE, END_DATE)
    quantity = random.randint(1, 500)
    unit_price = round(random.uniform(50, 5000), 2)
    total_amount = round(quantity * unit_price, 2)

    po = {
        "POID":          f"PO{str(i+1).zfill(5)}",        # e.g., PO00001
        "VendorID":      random.choice(vendor_ids),
        "Material":      random.choice(materials),
        "Department":    random.choice(departments),
        "Quantity":      quantity,
        "UnitPrice":     unit_price,
        "TotalAmount":   total_amount,
        "Currency":      "USD",
        "PODate":        po_date.strftime("%Y-%m-%d"),
        "ExpectedDelivery": (po_date + timedelta(days=random.randint(7, 45))).strftime("%Y-%m-%d"),
        "POStatus":      random.choice(["Approved", "Approved", "Approved", "Pending", "Cancelled"]),
        "PlantCode":     random.choice(["PLANT01", "PLANT02", "PLANT03", "PLANT04"]),
        "PurchasingGroup": random.choice(["PG001", "PG002", "PG003"])
    }
    purchase_orders.append(po)

df_po = pd.DataFrame(purchase_orders)

# ─────────────────────────────────────────────────────────────────────
# DATASET 3: GOODS RECEIPTS (GR)
# Purpose: Confirmation that ordered goods were actually received.
# SAP Equivalent: Goods Receipt (Transaction MIGO - Movement Type 101)
# ─────────────────────────────────────────────────────────────────────
print("📥 Creating Goods Receipts dataset...")

goods_receipts = []
approved_pos = [po for po in purchase_orders if po["POStatus"] == "Approved"]

for i, po in enumerate(approved_pos[:250]):  # 250 goods receipts
    po_date = datetime.strptime(po["PODate"], "%Y-%m-%d")
    expected = datetime.strptime(po["ExpectedDelivery"], "%Y-%m-%d")

    # Actual delivery: sometimes early, on-time, or delayed
    delay_days = random.randint(-5, 20)          # Negative = early, positive = late
    actual_delivery = expected + timedelta(days=delay_days)
    actual_delivery = min(actual_delivery, END_DATE)  # Can't be beyond our data range

    received_qty = int(po["Quantity"] * random.uniform(0.8, 1.0))  # 80–100% received

    gr = {
        "GRID":             f"GR{str(i+1).zfill(5)}",
        "POID":             po["POID"],
        "VendorID":         po["VendorID"],
        "ReceivedDate":     actual_delivery.strftime("%Y-%m-%d"),
        "ExpectedDate":     po["ExpectedDelivery"],
        "ReceivedQuantity": received_qty,
        "OrderedQuantity":  po["Quantity"],
        "GRStatus":         "Posted",
        "StorageLocation":  random.choice(["SL01", "SL02", "SL03"]),
        "InspectionResult": random.choice(["Passed", "Passed", "Passed", "Failed", "Partial"])
    }
    goods_receipts.append(gr)

df_gr = pd.DataFrame(goods_receipts)

# ─────────────────────────────────────────────────────────────────────
# DATASET 4: INVOICES
# Purpose: Bills sent by vendors after delivering goods.
# SAP Equivalent: Invoice Verification (Transaction MIRO/FB60)
# ─────────────────────────────────────────────────────────────────────
print("🧾 Creating Invoices dataset...")

invoices = []
for i, gr in enumerate(goods_receipts[:230]):  # 230 invoices
    gr_date = datetime.strptime(gr["ReceivedDate"], "%Y-%m-%d")
    invoice_date = gr_date + timedelta(days=random.randint(1, 10))   # Vendor sends bill 1-10 days after delivery
    invoice_date = min(invoice_date, END_DATE)

    # Get PO details for amount calculation
    matching_po = next((po for po in purchase_orders if po["POID"] == gr["POID"]), None)
    if matching_po:
        invoice_amount = round(gr["ReceivedQuantity"] * matching_po["UnitPrice"], 2)
        tax_amount = round(invoice_amount * 0.18, 2)   # 18% GST/Tax
        total_payable = round(invoice_amount + tax_amount, 2)
    else:
        invoice_amount = 10000
        tax_amount = 1800
        total_payable = 11800

    invoice = {
        "InvoiceID":      f"INV{str(i+1).zfill(5)}",
        "POID":           gr["POID"],
        "GRID":           gr["GRID"],
        "VendorID":       gr["VendorID"],
        "InvoiceDate":    invoice_date.strftime("%Y-%m-%d"),
        "InvoiceAmount":  invoice_amount,
        "TaxAmount":      tax_amount,
        "TotalPayable":   total_payable,
        "Currency":       "USD",
        "InvoiceStatus":  random.choice(["Approved", "Approved", "Approved", "Pending", "Disputed"]),
        "DueDate":        (invoice_date + timedelta(days=random.randint(30, 60))).strftime("%Y-%m-%d"),
        "PaymentTerms":   random.choice(payment_terms)
    }
    invoices.append(invoice)

df_invoices = pd.DataFrame(invoices)

# ─────────────────────────────────────────────────────────────────────
# DATASET 5: PAYMENTS
# Purpose: Actual money transferred to vendors.
# SAP Equivalent: Payment Run (Transaction F110 / FBZ2)
# ─────────────────────────────────────────────────────────────────────
print("💳 Creating Payments dataset...")

payments = []
approved_invoices = [inv for inv in invoices if inv["InvoiceStatus"] == "Approved"]

for i, inv in enumerate(approved_invoices):
    due_date = datetime.strptime(inv["DueDate"], "%Y-%m-%d")

    # Some payments are on-time, some late
    payment_delay = random.randint(-5, 30)   # Negative = early payment (discount earned!)
    payment_date = due_date + timedelta(days=payment_delay)
    payment_date = min(payment_date, END_DATE)

    discount_applied = 0
    if payment_delay <= 10 and inv["PaymentTerms"] == "2/10NET30":
        discount_applied = round(inv["TotalPayable"] * 0.02, 2)  # 2% early payment discount

    amount_paid = round(inv["TotalPayable"] - discount_applied, 2)

    payment = {
        "PaymentID":      f"PAY{str(i+1).zfill(5)}",
        "InvoiceID":      inv["InvoiceID"],
        "VendorID":       inv["VendorID"],
        "PaymentDate":    payment_date.strftime("%Y-%m-%d"),
        "DueDate":        inv["DueDate"],
        "AmountPaid":     amount_paid,
        "DiscountTaken":  discount_applied,
        "PaymentMethod":  random.choice(["Bank Transfer", "Cheque", "ACH", "Wire Transfer"]),
        "BankAccount":    f"ACC{random.randint(100000, 999999)}",
        "PaymentStatus":  "Completed",
        "CostCenter":     random.choice(["CC100", "CC200", "CC300", "CC400"])
    }
    payments.append(payment)

df_payments = pd.DataFrame(payments)

# ─────────────────────────────────────────────────────────────────────
# SAVE ALL DATASETS TO CSV FILES
# ─────────────────────────────────────────────────────────────────────
output_path = "/home/claude/P2P_Analytics_System/data/raw"

df_vendors.to_csv(f"{output_path}/vendors.csv", index=False)
df_po.to_csv(f"{output_path}/purchase_orders.csv", index=False)
df_gr.to_csv(f"{output_path}/goods_receipts.csv", index=False)
df_invoices.to_csv(f"{output_path}/invoices.csv", index=False)
df_payments.to_csv(f"{output_path}/payments.csv", index=False)

# ─────────────────────────────────────────────────────────────────────
# PRINT SUMMARY
# ─────────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("✅  ALL DATASETS CREATED SUCCESSFULLY!")
print("="*55)
print(f"📁 Vendors:         {len(df_vendors):>5} rows  | {len(df_vendors.columns)} columns")
print(f"📁 Purchase Orders: {len(df_po):>5} rows  | {len(df_po.columns)} columns")
print(f"📁 Goods Receipts:  {len(df_gr):>5} rows  | {len(df_gr.columns)} columns")
print(f"📁 Invoices:        {len(df_invoices):>5} rows  | {len(df_invoices.columns)} columns")
print(f"📁 Payments:        {len(df_payments):>5} rows  | {len(df_payments.columns)} columns")
print(f"\n📂 Files saved to: {output_path}")
print("="*55)
