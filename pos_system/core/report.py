from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ReportRepository(Protocol):
    def get(self) -> Report:
        pass


@dataclass
class Report:
    n_receipts: int
    revenue: float
