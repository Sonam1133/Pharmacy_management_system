from database.db_setup import get_connection
from datetime import datetime

def record_sale(medicine_id, quantity, customer_name=""):
    """Record a sale. Returns True on success, False if stock is insufficient."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, price, stock FROM medicines WHERE id = ?", (medicine_id,))
        med = cursor.fetchone()
        if not med or med['stock'] < quantity:
            return False

        total = med['price'] * quantity
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Atomic transaction: update stock AND insert sale record
        cursor.execute("UPDATE medicines SET stock = stock - ? WHERE id = ?", (quantity, medicine_id))
        cursor.execute('''
            INSERT INTO sales (medicine_id, medicine_name, quantity, unit_price, total_amount, sale_date, customer_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (medicine_id, med['name'], quantity, med['price'], total, now, customer_name))

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_all_sales():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM sales ORDER BY sale_date DESC").fetchall()
    conn.close()
    return rows
