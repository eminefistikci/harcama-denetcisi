from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date
from typing import Literal, Any
from decimal import Decimal


class Transaction(BaseModel):
    model_config = ConfigDict(frozen = True, str_strip_whitespace= True, extra = "ignore")

    transaction_id: str = Field(min_length=1)
    transaction_date: date
    description: str | None = None
    merchant: str = Field(min_length=1)
    category: str = Field(min_length=1)
    transaction_type: Literal["expense", "income", "refund"]
    amount: Decimal = Field(gt = 0)
    currency: str
    payment_method: str | None = None
    city: str | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 3:
            raise ValueError("Length of currency must be 3.")
        return value


class RejectedRow(BaseModel):
    row_number: int
    row_data: dict[str, Any]
    error_messages: list[str]


class CurrencySummary(BaseModel):
    transaction_count : int
    total_expense: Decimal
    total_income: Decimal
    total_refund: Decimal
    net_expense: Decimal
    cash_flow: Decimal
    max_expense: Decimal | None =None
    top_category: str | None = None
    start_date: date | None
    end_date: date | None
    currency: str

