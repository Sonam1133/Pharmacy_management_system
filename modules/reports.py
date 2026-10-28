"""Reporting and analytics using only the Python standard library."""
import sqlite3
from database.db_setup import get_connection


def get_top_selling(limit=5):
    """Return [(medicine_name, total_qty, total_revenue), ...] sorted by qty desc."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT medicine_name,
               SUM(quantity)     AS total_qty,
               SUM(total_amount) AS total_revenue
        FROM sales
        GROUP BY medicine_name
        ORDER BY total_qty DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [(r["medicine_name"], r["total_qty"], r["total_revenue"]) for r in rows]


def get_daily_totals(days=7):
    """Return [(date_str, revenue), ...] for the last N days, newest first."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT DATE(sale_date) AS day,
               SUM(total_amount) AS revenue
        FROM sales
        GROUP BY day
        ORDER BY day DESC
        LIMIT ?
    ''', (days,)).fetchall()
    conn.close()
    return [(r["day"], r["revenue"]) for r in rows]


def get_summary():
    """Return overall KPIs as a dict."""
    conn = get_connection()
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(total_amount), 0) FROM sales"
    ).fetchone()[0]
    sales_count = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    medicines   = conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
    low_stock   = conn.execute(
        "SELECT COUNT(*) FROM medicines WHERE stock <= 10"
    ).fetchone()[0]
    conn.close()
    return {
        "revenue": total_revenue,
        "sales_count": sales_count,
        "medicines": medicines,
        "low_stock": low_stock,
    }
