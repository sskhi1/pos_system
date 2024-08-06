from dataclasses import dataclass
from typing import Any

import pytest
from fastapi.testclient import TestClient

from pos_system.infra.repository import ReportDB
from pos_system.runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


@dataclass
class Fake:
    def report(self) -> dict[str, Any]:
        db = ReportDB()
        report = db.get()
        return {"n_receipts": report.n_receipts, "revenue": report.revenue}


def test_should_return_sales_report(client: TestClient) -> None:
    report = Fake().report()
    response = client.get("/sales")

    assert response.status_code == 200
    assert response.json() == {"sales": {**report}}
