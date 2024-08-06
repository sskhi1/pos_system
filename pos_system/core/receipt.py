from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol
from uuid import UUID, uuid4


class ReceiptRepository(Protocol):
    def create(self) -> Receipt:
        pass

    def add_product(self, receipt_id: UUID, product_id: UUID, quantity: int) -> Receipt:
        pass

    def get(self, receipt_id: UUID) -> Receipt:
        pass

    def close(self, receipt_id: UUID) -> None:
        pass

    def delete(self, receipt_id: UUID) -> None:
        pass


@dataclass
class Receipt:
    status: str
    products: List[ReceiptProduct]
    total: float

    id: UUID = field(default_factory=uuid4)


@dataclass
class ReceiptProduct:
    id: UUID
    quantity: int
    price: float
    total: float
