import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection
from uuid import UUID

from pos_system.core.errors import (
    DoesNotExistError,
    ExistsError,
    ParameterDoesNotExistError,
)
from pos_system.core.products import Product


@dataclass
class ProductsDB:
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

    def create(self, product: Product) -> Product:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()
            select = """
                SELECT * from products WHERE barcode =?
            """
            cursor.execute(select, (product.barcode,))
            u = cursor.fetchone()
            print(u)
            if u:
                raise KeyError

            select = """
                SELECT * from units WHERE uuid =?
                """
            cursor.execute(select, (str(product.unit_id),))
            u = cursor.fetchone()
            print(u)
            if not u:
                raise ParameterDoesNotExistError

            insert_unit_sql = """
                INSERT INTO products (uuid, unit_id, name, barcode, price)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(
                insert_unit_sql,
                (
                    str(product.id),
                    str(product.unit_id),
                    product.name,
                    product.barcode,
                    product.price,
                ),
            )
            conn.commit()

            print("Product created successfully.")
            return product
        except KeyError:
            raise ExistsError(product)
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def get(self, product_id: UUID) -> Product:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_unit_sql = """
                SELECT uuid, unit_id, name, barcode, price FROM products WHERE uuid = ?
            """

            cursor.execute(select_unit_sql, (str(product_id),))
            product_data = cursor.fetchone()

            if product_data:
                return Product(
                    product_data[1],
                    product_data[2],
                    product_data[3],
                    product_data[4],
                    product_data[0],
                )
            else:
                raise DoesNotExistError()
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def get_all(self) -> list[Product]:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_all_products_sql = """
                SELECT uuid, unit_id, name, barcode, price FROM products
            """

            cursor.execute(select_all_products_sql)
            products_data = cursor.fetchall()

            products = []
            for product_data in products_data:
                products.append(
                    Product(
                        product_data[1],
                        product_data[2],
                        product_data[3],
                        product_data[4],
                        product_data[0],
                    )
                )
            return products
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def update_price(self, product_id: UUID, new_price: float) -> None:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()
            select = """
                SELECT * from products WHERE uuid =?
            """
            cursor.execute(select, (str(product_id),))
            u = cursor.fetchone()
            if u:
                update_price_sql = """
                            UPDATE products SET price = ? WHERE uuid = ?
                        """
                cursor.execute(
                    update_price_sql,
                    (
                        new_price,
                        str(product_id),
                    ),
                )
                conn.commit()
                print(f"Price updated successfully for product: {product_id}")
            else:
                raise DoesNotExistError()
        except KeyError:
            raise DoesNotExistError()
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def delete_product_by_id(self, product_id: str) -> None:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            cursor.execute("DELETE FROM products WHERE uuid = ?", (product_id,))
            conn.commit()
            print(f"Product deleted successfully, id: {product_id}")
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()
