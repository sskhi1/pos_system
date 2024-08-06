from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from pos_system.infra.repository import ProductsDB
from pos_system.runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


@dataclass
class Fake:
    def product(self) -> dict[str, Any]:
        return {
            "unit_id": "12c33cb8-9590-4a6e-9b59-5e3598d57e7c",
            "name": "ball",
            "barcode": "0100000",
            "price": 10.5,
        }

    def product_invalid_unit(self) -> dict[str, Any]:
        return {
            "unit_id": str(uuid4()),
            "name": "balls",
            "barcode": "0000000001",
            "price": 10.5,
        }


def test_should_not_get_unknown_product(client: TestClient) -> None:
    unknown_id = str(uuid4())

    response = client.get(f"/products/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": f"Product with id<{unknown_id}> does not exist."
    }


def test_should_get_known_product(client: TestClient) -> None:
    known_id = "28265140-c1a3-47c9-81a2-5fb05283ddc8"

    response = client.get(f"/products/{known_id}")

    assert response.status_code == 200
    assert response.json()["product"]["name"] == "brinji"


def test_get_all_products(client: TestClient) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()["products"]) == 2


def test_create_and_update_product_price(client: TestClient) -> None:
    product_data = Fake().product()
    invalid_unit_product = Fake().product_invalid_unit()

    response = client.post("/products", json=product_data)
    product_id = response.json()["product"]["id"]

    assert response.status_code == 201
    assert response.json()["product"]["name"] == product_data["name"]

    response = client.post("/products", json=product_data)

    assert response.status_code == 409
    assert response.json() == {
        "message": "Product with barcode<0100000> already exist."
    }

    response = client.post("/products", json=invalid_unit_product)
    invalid_unit_id = invalid_unit_product["unit_id"]

    assert response.status_code == 404
    assert response.json() == {
        "message": f"Unit with id<{invalid_unit_id}> does not exist."
    }

    new_price = 99.99

    response = client.patch(f"/products/{product_id}", json={"new_price": new_price})

    assert response.status_code == 200

    known_id = product_id

    response = client.get(f"/products/{known_id}")

    assert response.status_code == 200
    assert response.json()["product"]["name"] == "ball"
    assert response.json()["product"]["price"] == new_price

    products_db = ProductsDB()
    products_db.delete_product_by_id(product_id)


def test_update_unknown_id(client: TestClient) -> None:
    unknown_id = str(uuid4())

    response = client.patch(f"/products/{unknown_id}", json={"new_price": 10000})

    assert response.status_code == 404
    assert response.json() == {
        "message": f"Product with id<{unknown_id}> does not exist."
    }
