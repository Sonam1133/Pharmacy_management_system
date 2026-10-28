from database.db_setup import get_connection

LOW_STOCK_THRESHOLD = 10

def add_medicine(name, company, category, batch_no, expiry_date, price, stock, prescription):
    conn = get_connection()
    conn.execute('''
        INSERT INTO medicines (name, company, category, batch_no, expiry_date, price, stock, prescription_required)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, company, category, batch_no, expiry_date, price, stock, int(prescription)))
    conn.commit()
    conn.close()

def get_all_medicines():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM medicines").fetchall()
    conn.close()
    return rows

def update_stock(medicine_id, new_stock):
    conn = get_connection()
    conn.execute("UPDATE medicines SET stock = ? WHERE id = ?", (new_stock, medicine_id))
    conn.commit()
    conn.close()

def get_low_stock_medicines():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM medicines WHERE stock <= ?", (LOW_STOCK_THRESHOLD,)
    ).fetchall()
    conn.close()
    return rows
