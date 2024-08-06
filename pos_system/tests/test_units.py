from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from pos_system.infra.repository import UnitsDB
from pos_system.runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


@dataclass
class Fake:
    def unit(self) -> dict[str, Any]:
        return {
            "name": "Tons",
        }


def test_should_not_get_unknown_unit(client: TestClient) -> None:
    unknown_id = str(uuid4())

    response = client.get(f"/units/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {"message": f"Unit with id<{unknown_id}> does not exist."}


def test_should_get_known_unit(client: TestClient) -> None:
    known_id = UUID("a22c734a-d034-4527-81df-c29b42dfd2f9")

    response = client.get(f"/units/{known_id}")

    assert response.status_code == 200
    assert response.json() == {
        "unit": {"id": "a22c734a-d034-4527-81df-c29b42dfd2f9", "name": "kg"}
    }


def test_should_create_unit_and_get_all(client: TestClient) -> None:
    unit_data = Fake().unit()

    response = client.post("/units", json=unit_data)

    assert response.status_code == 201
    assert response.json()["unit"]["name"] == unit_data["name"]

    response = client.get("/units")

    assert response.status_code == 200
    assert len(response.json()["units"]) == 3

    response = client.post("/units", json=unit_data)
    name = unit_data["name"]

    assert response.status_code == 409
    assert response.json() == {"message": f"Unit with name<{name}> already exist."}

    unit_db = UnitsDB()
    unit_db.delete_unit_by_name(name)
