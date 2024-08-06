from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


class UnitRepository(Protocol):
    def create(self, unit: Unit) -> Unit:
        pass

    def get(self, unit_id: UUID) -> Unit:
        pass

    def get_all(self) -> list[Unit]:
        pass


@dataclass
class Unit:
    name: str

    id: UUID = field(default_factory=uuid4)
