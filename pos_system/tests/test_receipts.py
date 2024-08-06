from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from pos_system.infra.repository import ReceiptsDB
from pos_system.runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


@pytest.fixture
def receipts_db() -> ReceiptsDB:
    return ReceiptsDB()


def test_should_not_get_unknown_receipt(
    client: TestClient, receipts_db: ReceiptsDB
) -> None:
    unknown_id = str(uuid4())

    response = client.get(f"/receipts/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": f"Receipt with id<{unknown_id}> does not exist."
    }


def test_should_get_known_receipt(client: TestClient, receipts_db: ReceiptsDB) -> None:
    known_id = "e7ea17cc-7d62-4556-9b04-7713cae427bf"

    response = client.get(f"/receipts/{known_id}")

    assert response.status_code == 200
    assert response.json()["receipt"]["id"] == known_id
    assert response.json()["receipt"]["status"] == "closed"


def test_create_receipt(client: TestClient, receipts_db: ReceiptsDB) -> None:
    response = client.post("/receipts")

    assert response.status_code == 201
    assert "receipt" in response.json()
    assert "id" in response.json()["receipt"]

    receipt_id = response.json()["receipt"]["id"]

    response = client.delete(f"/receipts/{receipt_id}")

    assert response.status_code == 200


def test_add_product_to_receipt(client: TestClient, receipts_db: ReceiptsDB) -> None:
    response = client.post("/receipts")

    assert response.status_code == 201
    assert "receipt" in response.json()
    assert "id" in response.json()["receipt"]

    known_receipt_id = response.json()["receipt"]["id"]
    unknown_receipt_id = str(uuid4())

    unknown_product_id = str(uuid4())
    unknown_product_data = {"id": unknown_product_id, "quantity": 2}

    known_product = {
        "id": str(UUID("28265140-c1a3-47c9-81a2-5fb05283ddc8")),
        "quantity": 2,
    }

    response = client.post(
        f"/receipts/{unknown_receipt_id}/products", json=known_product
    )

    assert response.status_code == 404
    assert response.json() == {
        "message": f"Receipt with id<{unknown_receipt_id}> does not exist."
    }

    response = client.post(
        f"/receipts/{known_receipt_id}/products", json=unknown_product_data
    )

    assert response.status_code == 404
    assert response.json() == {
        "message": f"Product with id<{unknown_product_id}> does not exist."
    }

    response = client.post(f"/receipts/{known_receipt_id}/products", json=known_product)

    assert response.status_code == 201
    assert len(response.json()["receipt"]["products"]) == 1

    response = client.post(f"/receipts/{known_receipt_id}/products", json=known_product)
    assert response.status_code == 201
    assert len(response.json()["receipt"]["products"]) == 1
    assert response.json()["receipt"]["products"][0]["quantity"] == 4

    response = client.delete(f"/receipts/{known_receipt_id}")

    assert response.status_code == 200


def test_close_receipt(client: TestClient, receipts_db: ReceiptsDB) -> None:
    receipt_id = str(uuid4())

    response = client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})

    assert response.status_code == 404
    assert response.json() == {
        "message": f"Receipt with id<{receipt_id}> does not exist."
    }


def test_delete_receipt_closed(client: TestClient, receipts_db: ReceiptsDB) -> None:
    receipt_id = "e7ea17cc-7d62-4556-9b04-7713cae427bf"

    response = client.delete(f"/receipts/{receipt_id}")

    assert response.status_code == 403
    assert response.json() == {"message": f"Receipt with id<{receipt_id}> is closed."}


def test_delete_receipt_does_not_exist(
    client: TestClient, receipts_db: ReceiptsDB
) -> None:
    receipt_id = uuid4()

    response = client.delete(f"/receipts/{receipt_id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": f"Receipt with id<{receipt_id}> does not exist."
    }
