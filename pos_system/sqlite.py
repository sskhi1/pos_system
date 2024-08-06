import sqlite3
from sqlite3 import Error


def create_connection(db_file: str) -> None:
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        create_units_table_sql = """
            CREATE TABLE IF NOT EXISTS units (
                uuid TEXT PRIMARY KEY,
                name TEXT
            );
        """

        create_products_table_sql = """
            CREATE TABLE IF NOT EXISTS products (
                uuid TEXT PRIMARY KEY,
                unit_id TEXT NOT NULL,
                name TEXT NOT NULL,
                barcode TEXT NOT NULL,
                price REAL NOT NULL
            );
        """

        create_report_table_sql = """
            CREATE TABLE IF NOT EXISTS sales_report (
                n_receipts INTEGER NOT NULL,
                revenue REAL NOT NULL
            );
        """

        create_receipts_table_sql = """
            CREATE TABLE IF NOT EXISTS receipts (
                id TEXT PRIMARY KEY,
                status TEXT,
                total FLOAT
            );
        """

        create_receipts_products_table_sql = """
            CREATE TABLE IF NOT EXISTS receipt_products (
                receipt_id TEXT,
                product_id TEXT,
                quantity INTEGER,
                FOREIGN KEY (receipt_id) REFERENCES receipts(id)
            );
        """

        cursor.execute(create_units_table_sql)
        cursor.execute(create_products_table_sql)
        cursor.execute(create_report_table_sql)
        cursor.execute(create_receipts_table_sql)
        cursor.execute(create_receipts_products_table_sql)

        cursor.execute("INSERT INTO sales_report (n_receipts, revenue) VALUES (0, 0)")
        conn.commit()
        print("Tables created successfully.")
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_connection(r".\pos_db.db")
