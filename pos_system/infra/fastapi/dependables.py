from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from pos_system.core.products import ProductRepository
from pos_system.core.receipt import ReceiptRepository
from pos_system.core.report import ReportRepository
from pos_system.core.units import UnitRepository


def get_units_repository(request: Request) -> UnitRepository:
    return request.app.state.units  # type: ignore


UnitsRepositoryDependable = Annotated[UnitRepository, Depends(get_units_repository)]


def get_products_repository(request: Request) -> ProductRepository:
    return request.app.state.products  # type: ignore


ProductsRepositoryDependable = Annotated[
    ProductRepository, Depends(get_products_repository)
]


def get_report_repository(request: Request) -> ReportRepository:
    return request.app.state.report  # type: ignore


ReportRepositoryDependable = Annotated[ReportRepository, Depends(get_report_repository)]


def get_receipt_repository(request: Request) -> ReceiptRepository:
    return request.app.state.receipts  # type: ignore


ReceiptRepositoryDependable = Annotated[
    ReceiptRepository, Depends(get_receipt_repository)
]
