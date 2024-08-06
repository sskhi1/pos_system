from fastapi import FastAPI

from pos_system.infra.fastapi import product_api, receipt_api, report_api, unit_api
from pos_system.infra.repository import ReceiptsDB, UnitsDB
from pos_system.infra.repository.products import ProductsDB
from pos_system.infra.repository.report import ReportDB


def init_app() -> FastAPI:
    app = FastAPI()
    app.include_router(unit_api)
    app.include_router(product_api)
    app.include_router(report_api)
    app.include_router(receipt_api)

    app.state.units = UnitsDB()
    app.state.products = ProductsDB()
    app.state.report = ReportDB()
    app.state.receipts = ReceiptsDB()

    return app
