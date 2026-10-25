from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    success: bool
    salesRepName: str


class CarSpecs(BaseModel):
    engine: str
    color: str


class CarSummary(BaseModel):
    carId: str
    model: str
    price: float
    specs: CarSpecs


class CatalogResponse(BaseModel):
    cars: list[CarSummary]


class EngineOptions(BaseModel):
    default: str
    selected: str


class CarDetailUnit(BaseModel):
    name: str
    value: str


class CarDetailInfo(BaseModel):
    engineOptions: EngineOptions
    units: list[CarDetailUnit]


class CarDetailResponse(BaseModel):
    carId: str
    details: CarDetailInfo


class CustomizationInput(BaseModel):
    engine: str | None = None
    color: str | None = None


class CartItemRequest(BaseModel):
    carId: str
    customizations: CustomizationInput


class AddToCartRequest(BaseModel):
    customerId: str
    piInfo: CartItemRequest


class AddToCartResponse(BaseModel):
    cartId: str


class BookingRequest(BaseModel):
    customerId: str
    carId: str


class BookingResponse(BaseModel):
    bookingId: str


class CustomInfoRequest(BaseModel):
    piInfo: Any | None = None


class CartItemSummary(BaseModel):
    carId: str
    customizations: CustomizationInput
    price: float


class CartInfoResponse(BaseModel):
    cartId: str
    items: list[CartItemSummary]


class OrderInfoResponse(BaseModel):
    bookingId: str
    carId: str
    customerId: str
    status: str
    confirmationDate: str


class CustomInfoResponse(BaseModel):
    cartInfo: dict[str, Any]
    orderInfo: dict[str, Any]
