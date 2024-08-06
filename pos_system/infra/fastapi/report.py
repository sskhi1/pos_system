from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from pos_system.core.report import Report
from pos_system.infra.fastapi.dependables import ReportRepositoryDependable

report_api = APIRouter(tags=["Report"])


class ReportModel(BaseModel):  # type: ignore
    n_receipts: int
    revenue: float


class ReportEnvelope(BaseModel):  # type: ignore
    sales: ReportModel


def map_report_to_model(report: Report) -> dict[str, Any]:
    return {"n_receipts": report.n_receipts, "revenue": report.revenue}


@report_api.get(
    "/sales", status_code=200, response_model=ReportEnvelope
)  # type: ignore
def get_sales_report(report: ReportRepositoryDependable) -> dict[str, Any]:
    report_data = report.get()
    return {"sales": ReportModel(**map_report_to_model(report_data))}
