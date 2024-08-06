import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection
from uuid import UUID

from pos_system.core.errors import DoesNotExistError, ExistsError
from pos_system.core.units import Unit


@dataclass
class UnitsDB:
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

    def create(self, unit: Unit) -> Unit:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()
            select = """
                SELECT * from units WHERE name =?
            """
            cursor.execute(select, (unit.name,))
            u = cursor.fetchone()
            print(u)
            if u:
                raise KeyError

            insert_unit_sql = """
                INSERT INTO units (uuid, name) VALUES (?, ?)
            """
            cursor.execute(insert_unit_sql, (str(unit.id), unit.name))
            conn.commit()

            print("Unit created successfully.")
            return unit
        except KeyError:
            raise ExistsError(unit)
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def get(self, unit_id: UUID) -> Unit:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_unit_sql = """
                SELECT uuid, name FROM units WHERE uuid = ?
            """

            cursor.execute(select_unit_sql, (str(unit_id),))
            unit_data = cursor.fetchone()

            if unit_data:
                return Unit(unit_data[1], unit_data[0])
            else:
                raise DoesNotExistError(unit_id)
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def get_all(self) -> list[Unit]:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            select_all_units_sql = """
                SELECT uuid, name FROM units
            """

            cursor.execute(select_all_units_sql)
            units_data = cursor.fetchall()

            units = []
            for unit_data in units_data:
                units.append(Unit(unit_data[1], UUID(unit_data[0])))
            return units
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()

    def delete_unit_by_name(self, name: str) -> None:
        try:
            conn = self.create_connection()
            if conn is None:
                raise sqlite3.Error
            cursor = conn.cursor()

            cursor.execute("DELETE FROM units WHERE name = ?", (name,))
            conn.commit()
            print(f"Unit deleted successfully: {name}")
        except sqlite3.Error as e:
            print(e)
            raise e
        finally:
            if conn:
                conn.close()
