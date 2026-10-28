import hashlib
from database.db_setup import get_connection

def hash_password(password: str) -> str:
    """Return the SHA-256 hex digest of a password."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str, role: str = 'staff') -> bool:
    """Register a new user. Returns True on success."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # username already exists
    finally:
        conn.close()

def authenticate(username: str, password: str):
    """Return (id, username, role) if credentials are valid, else None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()
    return row
