from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


class ProductRepository(Protocol):
    def create(self, product: Product) -> Product:
        pass

    def get(self, product_id: UUID) -> Product:
        pass

    def get_all(self) -> list[Product]:
        pass

    def update_price(self, product_id: UUID, new_price: float) -> None:
        pass


@dataclass
class Product:
    unit_id: UUID
    name: str
    barcode: str
    price: float

    id: UUID = field(default_factory=uuid4)
