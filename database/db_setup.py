"""
Database initialisation for the Pharmacy Management System.

Creates (or opens) pharmacy.db inside this folder and ensures the
required tables exist: users, medicines, sales.

Uses only Python's standard library (sqlite3).
"""

import os
import sqlite3

# Path to the database file — always lives beside this script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pharmacy.db")


def get_connection():
    """Return a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create all tables if they do not exist. Safe to run repeatedly."""
    conn = get_connection()
    cursor = conn.cursor()

    # ----- Users (login + role-based access) -----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            role          TEXT    NOT NULL CHECK(role IN ('admin', 'staff'))
        )
    """)

    # ----- Medicines (inventory) -----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            name                   TEXT    NOT NULL,
            company                TEXT,
            category               TEXT,
            batch_no               TEXT,
            expiry_date            TEXT,
            price                  REAL    NOT NULL,
            stock                  INTEGER NOT NULL DEFAULT 0,
            prescription_required  INTEGER DEFAULT 0
        )
    """)

    # ----- Sales (transaction log — snapshot of medicine at sale time) -----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id    INTEGER,
            medicine_name  TEXT    NOT NULL,
            quantity       INTEGER NOT NULL,
            unit_price     REAL    NOT NULL,
            total_amount   REAL    NOT NULL,
            sale_date      TEXT    NOT NULL,
            customer_name  TEXT,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    # Helpful indexes for reporting
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_med   ON sales(medicine_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date  ON sales(sale_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_med_name    ON medicines(name)")

    conn.commit()
    conn.close()
    print(f"Database initialised successfully at: {DB_PATH}")


if __name__ == "__main__":
    initialize_database()
