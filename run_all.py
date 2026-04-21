"""
MASTER SCRIPT: Run All Steps
==============================
Run this single script to execute the entire P2P Analytics pipeline
from scratch. Takes about 30-60 seconds to complete.

Usage: python run_all.py
"""

import subprocess
import sys
import time

scripts = [
    ("01_generate_datasets.py",   "📦 Generating Datasets"),
    ("02_data_processing.py",     "🧹 Cleaning & Merging Data"),
    ("03_kpi_calculations.py",    "📊 Calculating KPIs"),
    ("04_advanced_analytics.py",  "🔬 Running Advanced Analytics"),
    ("05_generate_charts.py",     "🎨 Generating Charts"),
]

print("=" * 60)
print("  P2P ANALYTICS SYSTEM — MASTER PIPELINE")
print("=" * 60)
print(f"  Starting at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

all_success = True
for script, description in scripts:
    print(f"\n▶  {description}...")
    start = time.time()
    result = subprocess.run(
        [sys.executable, f"scripts/{script}"],
        capture_output=True, text=True
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"   ✅ Completed in {elapsed:.1f}s")
    else:
        print(f"   ❌ FAILED: {result.stderr[-200:]}")
        all_success = False

print("\n" + "=" * 60)
if all_success:
    print("🎉  ALL STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nOutput files:")
    print("data/raw/           — 5 raw CSV datasets")
    print("data/processed/     — 5 cleaned datasets")
    print("data/final/         — p2p_master_dataset.csv")
    print("outputs/kpis/       — 10 KPI analysis files")
    print("outputs/charts/     — 5 chart PNG images")
    print("\nNext step: Open Power BI Desktop and import:")
    print("  → data/final/p2p_master_dataset.csv")
    print("  → outputs/kpis/*.csv")
else:
    print("SOME STEPS FAILED — check errors above")
print("=" * 60)
