import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection

from pos_system.core.report import Report


@dataclass
class ReportDB:
    db_file: str

    def __init__(self) -> None:
        self.db_file = "../pos_db.db"

    def create_connection(self) -> Connection | None:
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except sqlite3.Error as e:
            print(e)
            return None

    def get(self) -> Report:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_report_sql = """
                SELECT n_receipts, revenue FROM sales_report
            """

            cursor.execute(select_report_sql)
            sales_data = cursor.fetchone()

            if sales_data is None:
                cursor.execute(
                    "INSERT INTO sales_report (n_receipts, revenue) VALUES (0, 0)"
                )
                sales_data = [0, 0]

            return Report(sales_data[0], sales_data[1])
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()
