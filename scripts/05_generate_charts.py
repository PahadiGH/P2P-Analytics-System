"""
SCRIPT 5: Chart Generation
===========================
Creates professional charts that can be used in your project report
and as examples of what the Power BI dashboard will show.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")   # Non-interactive backend (for server)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

CHARTS_PATH = "/home/claude/P2P_Analytics_System/outputs/charts"
KPI_PATH    = "/home/claude/P2P_Analytics_System/outputs/kpis"

# Color palette
COLORS = ["#1a73e8", "#34a853", "#fbbc04", "#ea4335", "#9c27b0", "#00bcd4",
          "#ff5722", "#795548", "#607d8b", "#e91e63"]

plt.rcParams.update({
    "font.family":    "DejaVu Sans",
    "font.size":      10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
    "axes.facecolor":   "#f8f9fa",
    "axes.grid":        True,
    "grid.alpha":       0.3
})

print("🎨 Generating charts...")

# ── Load data ──
df_spend_cat  = pd.read_csv(f"{KPI_PATH}/kpi1_spend_by_category.csv")
df_spend_month= pd.read_csv(f"{KPI_PATH}/kpi1_spend_by_month.csv")
df_vendor     = pd.read_csv(f"{KPI_PATH}/kpi2_vendor_performance.csv")
df_delay      = pd.read_csv(f"{KPI_PATH}/kpi3_delay_distribution.csv")
df_trend      = pd.read_csv(f"{KPI_PATH}/spend_trend_analysis.csv")
df_risk       = pd.read_csv(f"{KPI_PATH}/vendor_risk_scores.csv")


# ─────────────────────────────────────────────
# CHART 1: Spend by Category (Horizontal Bar)
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
df_sc = df_spend_cat.sort_values("TotalSpend")
bars = ax.barh(df_sc["Category"], df_sc["TotalSpend"] / 1_000_000,
               color=COLORS[:len(df_sc)], edgecolor="white")
ax.set_xlabel("Total Spend (USD Millions)")
ax.set_title("📊 Total Procurement Spend by Category")
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
            f"${width:.1f}M", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHARTS_PATH}/chart1_spend_by_category.png", dpi=150)
plt.close()
print("  ✅ Chart 1: Spend by Category")


# ─────────────────────────────────────────────
# CHART 2: Monthly Spend Trend (Line Chart)
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
df_trend_sorted = df_trend.sort_values(["POYear", "POMonth"])
x_labels = [f"{int(r['POYear'])}-{int(r['POMonth']):02d}"
             for _, r in df_trend_sorted.iterrows()]
ax.plot(x_labels, df_trend_sorted["TotalSpend"] / 1_000_000,
        marker="o", linewidth=2.5, color="#1a73e8", markersize=5)
ax.fill_between(x_labels, df_trend_sorted["TotalSpend"] / 1_000_000,
                alpha=0.15, color="#1a73e8")
ax.plot(x_labels, df_trend_sorted["Rolling3MonthAvg"] / 1_000_000,
        linestyle="--", linewidth=1.5, color="#ea4335", label="3-Month Rolling Avg")
ax.set_xlabel("Month")
ax.set_ylabel("Spend (USD Millions)")
ax.set_title("📈 Monthly Procurement Spend Trend (2023–2024)")
ax.set_xticks(range(0, len(x_labels), 2))
ax.set_xticklabels(x_labels[::2], rotation=45, ha="right")
ax.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS_PATH}/chart2_monthly_spend_trend.png", dpi=150)
plt.close()
print("  ✅ Chart 2: Monthly Spend Trend")


# ─────────────────────────────────────────────
# CHART 3: Vendor Performance Scores (Bar)
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
df_vp = df_vendor.sort_values("VendorScore", ascending=False).head(15)
colors_bar = ["#34a853" if s >= 70 else "#fbbc04" if s >= 55 else "#ea4335"
              for s in df_vp["VendorScore"]]
bars = ax.bar(range(len(df_vp)), df_vp["VendorScore"], color=colors_bar, edgecolor="white")
ax.set_xticks(range(len(df_vp)))
ax.set_xticklabels(
    [name.split()[0] for name in df_vp["VendorName"]],
    rotation=45, ha="right"
)
ax.axhline(y=70, color="#34a853", linestyle="--", alpha=0.7, label="Good (70)")
ax.axhline(y=55, color="#fbbc04", linestyle="--", alpha=0.7, label="Average (55)")
ax.set_ylim(0, 100)
ax.set_ylabel("Vendor Performance Score (0-100)")
ax.set_title("🏆 Vendor Performance Scorecard (Top 15 Vendors)")
for bar, score in zip(bars, df_vp["VendorScore"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f"{score:.0f}", ha="center", fontsize=8)
green_patch  = mpatches.Patch(color="#34a853", label="Good (≥70)")
yellow_patch = mpatches.Patch(color="#fbbc04", label="Average (55-70)")
red_patch    = mpatches.Patch(color="#ea4335", label="Poor (<55)")
ax.legend(handles=[green_patch, yellow_patch, red_patch])
plt.tight_layout()
plt.savefig(f"{CHARTS_PATH}/chart3_vendor_performance.png", dpi=150)
plt.close()
print("  ✅ Chart 3: Vendor Performance Scores")


# ─────────────────────────────────────────────
# CHART 4: Delivery Delay Distribution (Pie)
# ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: Pie chart
pie_colors = ["#34a853", "#1a73e8", "#fbbc04", "#ff9800", "#ea4335"]
wedges, texts, autotexts = axes[0].pie(
    df_delay["Count"],
    labels=df_delay["DelayCategory"],
    colors=pie_colors[:len(df_delay)],
    autopct="%1.1f%%",
    startangle=140,
    pctdistance=0.8
)
axes[0].set_title("🚚 Delivery Delay Distribution")

# Right: Vendor Risk scatter
axes[1].scatter(
    df_risk["LateDeliveryRate"] * 100,
    df_risk["TotalRiskScore"],
    c=[COLORS[i % len(COLORS)] for i in range(len(df_risk))],
    s=df_risk["TotalSpend"] / df_risk["TotalSpend"].max() * 300 + 30,
    alpha=0.7, edgecolors="white"
)
axes[1].set_xlabel("Late Delivery Rate (%)")
axes[1].set_ylabel("Total Risk Score")
axes[1].set_title("⚠️ Vendor Risk Map\n(Bubble size = Spend Volume)")
for _, row in df_risk.head(5).iterrows():
    axes[1].annotate(
        row["VendorName"].split()[0],
        (row["LateDeliveryRate"] * 100, row["TotalRiskScore"]),
        fontsize=7, ha="center"
    )

plt.tight_layout()
plt.savefig(f"{CHARTS_PATH}/chart4_delay_and_risk.png", dpi=150)
plt.close()
print("  ✅ Chart 4: Delay Distribution & Risk Map")


# ─────────────────────────────────────────────
# CHART 5: KPI Summary Dashboard Card (PNG)
# ─────────────────────────────────────────────
import json
with open(f"{KPI_PATH}/kpi_summary.json") as f:
    kpis = json.load(f)

fig, axes = plt.subplots(2, 4, figsize=(16, 6))
fig.suptitle("P2P Analytics — Executive KPI Dashboard", fontsize=16, fontweight="bold", y=1.02)

kpi_cards = [
    ("Total Spend",          f"${kpis['TotalSpendUSD']/1e6:.1f}M",   "#1a73e8"),
    ("Total Paid",           f"${kpis['TotalPaidUSD']/1e6:.1f}M",    "#34a853"),
    ("Avg Vendor Score",     f"{kpis['AvgVendorScore']:.1f}/100",     "#9c27b0"),
    ("Total Vendors",        f"{kpis['TotalVendors']}",               "#00bcd4"),
    ("On-Time Delivery",     f"{kpis['OnTimeDeliveryRate_Pct']:.1f}%","#fbbc04"),
    ("Avg Delivery Delay",   f"{kpis['AvgDeliveryDelay_Days']:.1f}d","#ea4335"),
    ("On-Time Payment",      f"{kpis['OnTimePaymentRate_Pct']:.1f}%", "#ff5722"),
    ("Avg Cycle Time",       f"{kpis['AvgCycleTime_Days']:.0f} days", "#607d8b"),
]

for ax, (title, value, color) in zip(axes.flat, kpi_cards):
    ax.set_facecolor(color)
    ax.text(0.5, 0.65, value, transform=ax.transAxes, ha="center", va="center",
            fontsize=22, fontweight="bold", color="white")
    ax.text(0.5, 0.2, title, transform=ax.transAxes, ha="center", va="center",
            fontsize=10, color="white", alpha=0.9)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

plt.tight_layout()
plt.savefig(f"{CHARTS_PATH}/chart5_kpi_dashboard_cards.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✅ Chart 5: KPI Dashboard Cards")

print(f"\n📂 All charts saved to: {CHARTS_PATH}/")
print("✅  CHART GENERATION COMPLETE!")
