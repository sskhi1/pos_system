import sqlite3
from sqlite3 import Error
from typing import Optional


class DatabaseManager:
    def __init__(self, db_file: str) -> None:
        self.db_file = db_file

    def create_connection(self) -> Optional[sqlite3.Connection]:
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    def clear_tables(self) -> None:
        tables = ["units", "products", "sales_report", "receipts", "receipt_products"]
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                conn.commit()
                print("Tables cleared successfully.")
            except Error as e:
                print(e)
            finally:
                conn.close()


if __name__ == "__main__":
    db_manager = DatabaseManager(r".\pos_db.db")
    db_manager.clear_tables()
