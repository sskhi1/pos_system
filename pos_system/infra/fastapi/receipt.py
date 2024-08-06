from typing import Any, List
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from pos_system.core.errors import (
    DoesNotExistError,
    ParameterDoesNotExistError,
    ReceiptAlreadyClosedError,
)
from pos_system.infra.fastapi.dependables import ReceiptRepositoryDependable

receipt_api = APIRouter(tags=["Receipts"])


class ReceiptProductModel(BaseModel):  # type: ignore
    id: UUID
    quantity: int
    price: float
    total: float


class ProductAddRequest(BaseModel):  # type: ignore
    id: UUID
    quantity: int


class ReceiptModel(BaseModel):  # type: ignore
    id: UUID
    status: str
    products: List[ReceiptProductModel]
    total: float


class ReceiptEnvelope(BaseModel):  # type: ignore
    receipt: ReceiptModel


class StatusUpdateRequest(BaseModel):  # type: ignore
    status: str


class StatusUpdateResponse(BaseModel):  # type: ignore
    pass


@receipt_api.post(
    "/receipts",
    status_code=201,
    response_model=ReceiptEnvelope,
)  # type: ignore
def create_receipt(receipts: ReceiptRepositoryDependable) -> dict[str, Any]:
    return {"receipt": receipts.create()}


@receipt_api.post(
    "/receipts/{receipt_id}/products",
    status_code=201,
    response_model=ReceiptEnvelope,
)  # type: ignore
def add_product(
    receipt_id: UUID, product: ProductAddRequest, receipts: ReceiptRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        receipts.add_product(receipt_id, product.id, product.quantity)
        return {"receipt": receipts.get(receipt_id)}
    except ParameterDoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Product with id<{product.id}> does not exist."},
        )
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Receipt with id<{receipt_id}> does not exist."},
        )


@receipt_api.get(
    "/receipts/{receipt_id}", status_code=200, response_model=ReceiptEnvelope
)  # type: ignore
def get_receipt(
    receipt_id: UUID, receipts: ReceiptRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        return {"receipt": receipts.get(receipt_id)}
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Receipt with id<{receipt_id}> does not exist."},
        )


@receipt_api.patch(
    "/receipts/{receipt_id}", status_code=200, response_model=StatusUpdateResponse
)  # type: ignore
def close_receipt(
    receipt_id: UUID,
    update_receipt: StatusUpdateRequest,
    receipts: ReceiptRepositoryDependable,
) -> StatusUpdateResponse | JSONResponse:
    try:
        receipts.close(receipt_id)
        return StatusUpdateResponse()
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Receipt with id<{receipt_id}> does not exist."},
        )


@receipt_api.delete(
    "/receipts/{receipt_id}", status_code=200, response_model=StatusUpdateResponse
)  # type: ignore
def delete_receipt(
    receipt_id: UUID, receipts: ReceiptRepositoryDependable
) -> StatusUpdateResponse | JSONResponse:
    try:
        receipts.delete(receipt_id)
        return StatusUpdateResponse()
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Receipt with id<{receipt_id}> does not exist."},
        )
    except ReceiptAlreadyClosedError:
        return JSONResponse(
            status_code=403,
            content={"message": f"Receipt with id<{receipt_id}> is closed."},
        )
