"""
Business Sales Analysis Pipeline
================================

Loads transactional sales data, computes business KPIs, and generates
executive-style chart visualizations for the consulting report.

Outputs:
    - Console KPI summary
    - output/kpi_report.json     (machine-readable KPIs)
    - output/monthly_revenue.png (revenue trend chart)
    - output/top_products.png    (top 10 products by revenue)
    - output/revenue_by_region.png (regional performance)
    - output/category_breakdown.png (category share of revenue)

Usage:
    pip install -r requirements.txt
    python analysis.py
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
DATA_PATH = Path("data/sales_data.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Consistent professional chart styling for executive reports
plt.style.use("seaborn-v0_8-whitegrid")
BRAND_COLOR = "#1F3A5F"
ACCENT_COLOR = "#2E75B6"


# ------------------------------------------------------------------
# Step 1 — Load & validate
# ------------------------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    """Load sales data and perform basic validation."""
    df = pd.read_csv(path, parse_dates=["order_date"])
    required = {"order_id", "customer_id", "region", "product",
                "category", "price", "quantity", "order_date"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")
    return df


# ------------------------------------------------------------------
# Step 2 — Compute KPIs
# ------------------------------------------------------------------
def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns used across analyses."""
    df = df.copy()
    df["revenue"] = df["price"] * df["quantity"]
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute the headline KPIs reported to the executive team."""
    total_revenue = float(df["revenue"].sum())
    total_orders = int(len(df))
    unique_customers = int(df["customer_id"].nunique())
    avg_order_value = float(df["revenue"].mean())

    top_product = (
        df.groupby("product")["revenue"].sum().idxmax()
    )
    top_region = (
        df.groupby("region")["revenue"].sum().idxmax()
    )
    top_category = (
        df.groupby("category")["revenue"].sum().idxmax()
    )

    return {
        "total_revenue_eur":  round(total_revenue, 2),
        "total_orders":       total_orders,
        "unique_customers":   unique_customers,
        "avg_order_value":    round(avg_order_value, 2),
        "top_product":        top_product,
        "top_region":         top_region,
        "top_category":       top_category,
    }


# ------------------------------------------------------------------
# Step 3 — Generate executive charts
# ------------------------------------------------------------------
def chart_monthly_revenue(df: pd.DataFrame) -> None:
    monthly = df.groupby("month")["revenue"].sum()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly.index, monthly.values,
            color=BRAND_COLOR, marker="o", linewidth=2.5)
    ax.fill_between(monthly.index, monthly.values,
                    color=ACCENT_COLOR, alpha=0.15)
    ax.set_title("Monthly Revenue Trend (2025)",
                 fontsize=14, fontweight="bold", color=BRAND_COLOR)
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (EUR)")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_revenue.png", dpi=130)
    plt.close()


def chart_top_products(df: pd.DataFrame) -> None:
    top = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=True)
        .tail(10)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top.index, top.values, color=ACCENT_COLOR)
    ax.set_title("Top Products by Revenue",
                 fontsize=14, fontweight="bold", color=BRAND_COLOR)
    ax.set_xlabel("Revenue (EUR)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "top_products.png", dpi=130)
    plt.close()


def chart_revenue_by_region(df: pd.DataFrame) -> None:
    by_region = (
        df.groupby("region")["revenue"].sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(by_region.index, by_region.values, color=BRAND_COLOR)
    ax.set_title("Revenue by Region",
                 fontsize=14, fontweight="bold", color=BRAND_COLOR)
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue (EUR)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "revenue_by_region.png", dpi=130)
    plt.close()


def chart_category_breakdown(df: pd.DataFrame) -> None:
    by_cat = df.groupby("category")["revenue"].sum()

    fig, ax = plt.subplots(figsize=(7, 7))
    colors = [BRAND_COLOR, ACCENT_COLOR, "#7FB3D5"]
    ax.pie(by_cat.values, labels=by_cat.index, autopct="%1.1f%%",
           colors=colors[:len(by_cat)], startangle=90,
           textprops={"fontsize": 11})
    ax.set_title("Revenue Share by Category",
                 fontsize=14, fontweight="bold", color=BRAND_COLOR)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "category_breakdown.png", dpi=130)
    plt.close()


# ------------------------------------------------------------------
# Step 4 — Orchestration
# ------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print(" SALES ANALYSIS — Executive Reporting Pipeline")
    print("=" * 60)

    df = load_data(DATA_PATH)
    df = enrich(df)
    print(f"Loaded {len(df)} transactions "
          f"({df['order_date'].min().date()} → "
          f"{df['order_date'].max().date()})")

    kpis = compute_kpis(df)
    print("\nHeadline KPIs:")
    for k, v in kpis.items():
        print(f"  {k:25s} {v}")

    print("\nGenerating executive charts...")
    chart_monthly_revenue(df)
    chart_top_products(df)
    chart_revenue_by_region(df)
    chart_category_breakdown(df)

    with open(OUTPUT_DIR / "kpi_report.json", "w") as f:
        json.dump(kpis, f, indent=2)

    print(f"\nOutputs written to ./{OUTPUT_DIR}/")
    print("Done.")


if __name__ == "__main__":
    main()
