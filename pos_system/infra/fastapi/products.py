from typing import Any
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from pos_system.core.errors import (
    DoesNotExistError,
    ExistsError,
    ParameterDoesNotExistError,
)
from pos_system.core.products import Product
from pos_system.infra.fastapi.dependables import ProductsRepositoryDependable

product_api = APIRouter(tags=["Products"])


class CreateProductRequest(BaseModel):  # type: ignore
    unit_id: UUID
    name: str
    barcode: str
    price: float


class ProductItem(BaseModel):  # type: ignore
    id: UUID
    unit_id: UUID
    name: str
    barcode: str
    price: float


class ProductEnvelope(BaseModel):  # type: ignore
    product: ProductItem


class ProductListEnvelope(BaseModel):  # type: ignore
    products: list[ProductItem]


class UpdateRequest(BaseModel):  # type: ignore
    new_price: float


class UpdateResponse(BaseModel):  # type: ignore
    pass


@product_api.post(
    "/products",
    status_code=201,
    response_model=ProductEnvelope,
)  # type: ignore
def create_product(
    request: CreateProductRequest, products: ProductsRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        product = Product(**request.model_dump())
        products.create(product)

        return {"product": product}
    except ExistsError:
        return JSONResponse(
            status_code=409,
            content={
                "message": f"Product with barcode<{request.barcode}> already exist."
            },
        )
    except ParameterDoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Unit with id<{request.unit_id}> does not exist."},
        )


@product_api.get(
    "/products/{product_id}",
    status_code=200,
    response_model=ProductEnvelope,
)  # type: ignore
def get_product(
    product_id: UUID, products: ProductsRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        return {"product": products.get(product_id)}
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Product with id<{product_id}> does not exist."},
        )


@product_api.get(
    "/products", status_code=200, response_model=ProductListEnvelope
)  # type: ignore
def get_all_products(products: ProductsRepositoryDependable) -> dict[str, Any]:
    return {"products": products.get_all()}


@product_api.patch(
    "/products/{product_id}", status_code=200, response_model=UpdateResponse
)  # type: ignore
def update_product(
    product_id: UUID,
    update_request: UpdateRequest,
    products: ProductsRepositoryDependable,
) -> UpdateResponse | JSONResponse:
    try:
        products.update_price(product_id, update_request.new_price)
        return UpdateResponse()
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Product with id<{product_id}> " f"does not exist."},
        )
