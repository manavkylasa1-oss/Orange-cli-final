from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    error: str
    detail: Any | None = None


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    username: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=1, max_length=128)
    firstname: str = Field(min_length=1, max_length=30)
    lastname: str = Field(min_length=1, max_length=30)
    balance: float = Field(ge=0)


class UpdateBalanceRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    username: str = Field(min_length=1, max_length=30)
    new_balance: float = Field(ge=0)


class CreatePortfolioRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str = Field(min_length=1, max_length=30)
    description: str = Field(default='', max_length=500)


class BuyTradeRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ticker: str = Field(min_length=1, max_length=10)
    portfolio_id: int = Field(gt=0)
    quantity: float = Field(gt=0)


class SellTradeRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ticker: str = Field(min_length=1, max_length=10)
    portfolio_id: int = Field(gt=0)
    quantity: float = Field(gt=0)


class GrantPortfolioAccessRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    user_id: str = Field(min_length=1, max_length=120)
    role: Literal['viewer', 'manager']


class RevokePortfolioAccessRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    user_id: str = Field(min_length=1, max_length=120)
