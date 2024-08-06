from typing import Any
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from pos_system.core.errors import DoesNotExistError, ExistsError
from pos_system.core.units import Unit
from pos_system.infra.fastapi.dependables import UnitsRepositoryDependable

unit_api = APIRouter(tags=["Units"])


class CreateUnitRequest(BaseModel):  # type: ignore
    name: str


class Unit_(BaseModel):  # type: ignore
    id: UUID
    name: str


class UnitEnvelope(BaseModel):  # type: ignore
    unit: Unit_


class UnitListEnvelope(BaseModel):  # type: ignore
    units: list[Unit_]


@unit_api.post(
    "/units",
    status_code=201,
    response_model=UnitEnvelope,
)  # type: ignore
def create_unit(
    request: CreateUnitRequest, units: UnitsRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        unit = Unit(**request.model_dump())
        units.create(unit)

        return {"unit": unit}
    except ExistsError:
        return JSONResponse(
            status_code=409,
            content={"message": f"Unit with name<{request.name}> already exist."},
        )


@unit_api.get(
    "/units/{unit_id}",
    status_code=200,
    response_model=UnitEnvelope,
)  # type: ignore
def get_unit(
    unit_id: UUID, units: UnitsRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        return {"unit": units.get(unit_id)}
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"message": f"Unit with id<{unit_id}> does not exist."},
        )


@unit_api.get(
    "/units", status_code=200, response_model=UnitListEnvelope
)  # type: ignore
def get_all_units(units: UnitsRepositoryDependable) -> dict[str, Any]:
    return {"units": units.get_all()}
