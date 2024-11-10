import sqlite3
from datetime import datetime
from contextlib import contextmanager


class OrderManager:
    def __init__(self, db_path="orders.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self.get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    ism TEXT,
                    razmer TEXT,
                    nomer TEXT,
                    file_id TEXT,
                    file_type TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def create_order(self, order_id: str, user_data: dict) -> bool:
        try:
            with self.get_db() as conn:
                conn.execute("""
                    INSERT INTO orders (
                        order_id, user_id, ism, razmer, nomer, 
                        file_id, file_type, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_id,
                    user_data['user_id'],
                    user_data['ism'],
                    user_data['razmer'],
                    user_data['nomer'],
                    user_data['file_id'],
                    user_data.get('file_type', 'photo'),
                    datetime.now()
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error creating order: {e}")
            return False

    def get_order(self, order_id: str) -> dict:
        with self.get_db() as conn:
            result = conn.execute(
                "SELECT * FROM orders WHERE order_id = ?",
                (order_id,)
            ).fetchone()
            return dict(result) if result else None

    def get_user_orders(self, user_id: int) -> list:
        with self.get_db() as conn:
            results = conn.execute(
                "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(row) for row in results]

    def update_order_status(self, order_id: str, status: str) -> bool:
        try:
            with self.get_db() as conn:
                conn.execute(
                    "UPDATE orders SET status = ? WHERE order_id = ?",
                    (status, order_id)
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False

    def delete_order(self, order_id: str) -> bool:
        try:
            with self.get_db() as conn:
                conn.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting order: {e}")
            return False

    def cleanup_old_orders(self, days=30):
        """Delete orders older than specified days"""
        try:
            with self.get_db() as conn:
                conn.execute("""
                    DELETE FROM orders 
                    WHERE datetime(created_at) < datetime('now', '-? days')
                """, (days,))
                conn.commit()
        except Exception as e:
            print(f"Error cleaning up old orders: {e}")

    def save_temp_order_data(self, order_id: str, user_data: dict) -> bool:
        """Saves temporary order data to the database."""
        try:
            with self.get_db() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO orders (
                        order_id, user_id, ism, razmer, nomer, file_id, file_type, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_id,
                    user_data['user_id'],
                    user_data['ism'],
                    user_data['razmer'],
                    user_data['nomer'],
                    user_data['file_id'],
                    user_data.get('file_type', 'photo'),
                    'pending',  # initial status
                    datetime.now()
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving temp order data: {e}")
            return False

    def get_temp_order_data(self, order_id: str) -> dict:
        """Retrieves temporary order data from the database."""
        with self.get_db() as conn:
            result = conn.execute(
                "SELECT * FROM orders WHERE order_id = ?",
                (order_id,)
            ).fetchone()
            return dict(result) if result else None

    def delete_temp_order_data(self, order_id: str) -> bool:
        """Deletes temporary order data from the database."""
        try:
            with self.get_db() as conn:
                conn.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting temp order data: {e}")
            return False