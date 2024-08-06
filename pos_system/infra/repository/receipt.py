import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection
from typing import List
from uuid import UUID, uuid4

from pos_system.core.errors import (
    DoesNotExistError,
    ParameterDoesNotExistError,
    ReceiptAlreadyClosedError,
)
from pos_system.core.receipt import Receipt, ReceiptProduct


@dataclass
class ReceiptsDB:
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

    def create(self) -> Receipt:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()
            u_id = uuid4()
            receipt = Receipt(id=u_id, status="open", total=0, products=[])

            insert_unit_sql = """
                INSERT INTO receipts (id, status, total) VALUES (?, ?, ?)
            """
            cursor.execute(
                insert_unit_sql, (str(receipt.id), receipt.status, receipt.total)
            )
            conn.commit()

            print("Receipt created successfully.")
            return receipt
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def add_product(self, receipt_id: UUID, product_id: UUID, quantity: int) -> None:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_receipt_sql = """
                SELECT id, status, total FROM receipts WHERE id = ?
            """

            cursor.execute(select_receipt_sql, (str(receipt_id),))
            product_data = cursor.fetchone()

            if not product_data:
                raise DoesNotExistError()
            products = self.get_receipt_products(receipt_id)
            total = product_data[2]

            select_unit_sql = """
                            SELECT price
                            FROM products WHERE uuid = ?
                        """

            cursor.execute(select_unit_sql, (str(product_id),))
            product_data = cursor.fetchone()

            if not product_data:
                raise ParameterDoesNotExistError()

            price = product_data[0]
            already_in_receipt = False

            for product in products:
                if product.id == str(product_id):
                    already_in_receipt = True
                    break

            if already_in_receipt:
                select_receipt_product_sql = """
                                SELECT quantity FROM receipt_products
                                WHERE receipt_id = ? AND product_id = ?
                            """
                cursor.execute(
                    select_receipt_product_sql, (str(receipt_id), str(product_id))
                )
                product_data = cursor.fetchone()
                quantity_ = product_data[0]
                total_quantity = quantity_ + quantity
                update_receipt_sql = """
                                        UPDATE receipt_products SET quantity = ?
                                        WHERE receipt_id = ? AND product_id = ?
                                    """
                cursor.execute(
                    update_receipt_sql,
                    (
                        total_quantity,
                        str(receipt_id),
                        str(product_id),
                    ),
                )
            else:
                insert_product_sql = """
                                INSERT INTO receipt_products
                                (receipt_id, product_id, quantity)
                                VALUES (?, ?, ?)
                            """
                cursor.execute(
                    insert_product_sql, (str(receipt_id), str(product_id), quantity)
                )
            total_ = total + quantity * price
            update_receipt_sql = """
                                UPDATE receipts SET total = ? WHERE id = ?
                            """
            cursor.execute(
                update_receipt_sql,
                (
                    total_,
                    str(receipt_id),
                ),
            )
            select_sales_sql = """
                                        SELECT n_receipts, revenue FROM sales_report
                                    """

            cursor.execute(select_sales_sql)
            sales_data = cursor.fetchone()
            if sales_data is None:
                cursor.execute(
                    "INSERT INTO sales_report (n_receipts, revenue) VALUES (0, 0)"
                )
                sales_data = [0, 0]

            # closed_receipts = sales_data[0]
            revenue = sales_data[1]

            update_sales_sql = """
                                                    UPDATE sales_report SET revenue = ?
                                                """
            cursor.execute(
                update_sales_sql,
                (revenue + quantity * price,),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def get(self, receipt_id: UUID) -> Receipt:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_receipt_sql = """
                SELECT id, status, total FROM receipts WHERE id = ?
            """

            cursor.execute(select_receipt_sql, (str(receipt_id),))
            product_data = cursor.fetchone()

            if product_data:
                return Receipt(
                    id=product_data[0],
                    products=self.get_receipt_products(receipt_id),
                    total=product_data[2],
                    status=product_data[1],
                )
            else:
                raise DoesNotExistError()
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def get_receipt_products(self, receipt_id: UUID) -> List[ReceiptProduct]:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_receipt_products_sql = """
                SELECT product_id, quantity FROM receipt_products WHERE receipt_id = ?
            """

            cursor.execute(select_receipt_products_sql, (str(receipt_id),))
            products = cursor.fetchall()
            product_list = []
            for product in products:
                select_unit_sql = """
                                SELECT price FROM products WHERE uuid = ?
                            """

                cursor.execute(select_unit_sql, (str(product[0]),))
                product_data = cursor.fetchone()
                price = product_data[0]
                total = price * product[1]

                res_product = ReceiptProduct(
                    id=product[0], quantity=product[1], price=price, total=total
                )
                product_list.append(res_product)

            return product_list
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def close(self, receipt_id: UUID) -> None:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_receipt_sql = """
                SELECT id, status, total FROM receipts WHERE id = ?
            """

            cursor.execute(select_receipt_sql, (str(receipt_id),))
            product_data = cursor.fetchone()

            if product_data:
                update_receipt_sql = """
                            UPDATE receipts SET status = ? WHERE id = ?
                        """
                cursor.execute(
                    update_receipt_sql,
                    (
                        "closed",
                        str(receipt_id),
                    ),
                )
                print(f"Status updated successfully for receipt: {receipt_id}")
            else:
                raise DoesNotExistError()

            select_sales_sql = """
                            SELECT n_receipts, revenue FROM sales_report
                        """

            cursor.execute(select_sales_sql)
            sales_data = cursor.fetchone()
            if sales_data is None:
                cursor.execute(
                    "INSERT INTO sales_report (n_receipts, revenue) VALUES (0, 0)"
                )
                sales_data = [0, 0]

            closed_receipts = sales_data[0]
            # revenue = sales_data[1]

            update_sales_sql = """
                                        UPDATE sales_report SET n_receipts = ?
                                    """
            cursor.execute(
                update_sales_sql,
                (closed_receipts + 1,),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def delete(self, receipt_id: UUID) -> None:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_receipt_sql = """
                SELECT id, status, total FROM receipts WHERE id = ?
            """

            cursor.execute(select_receipt_sql, (str(receipt_id),))
            product_data = cursor.fetchone()

            if product_data:
                if product_data[1] == "closed":
                    raise ReceiptAlreadyClosedError()
                cursor.execute("DELETE FROM receipts WHERE id = ?", (str(receipt_id),))
                cursor.execute(
                    "DELETE FROM receipt_products WHERE receipt_id = ?",
                    (str(receipt_id),),
                )
                conn.commit()
                print(f"Receipt deleted successfully successfully: {receipt_id}")
            else:
                raise DoesNotExistError()
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()
