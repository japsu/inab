from datetime import date as date_type

from pydantic import BaseModel, Field


class ScheduledTransaction(BaseModel):
    date: date_type
    cents: int
    description: str

    class Config:
        frozen = True


class Actual(BaseModel):
    account_balance_cents: int
    scheduled_transactions: list[ScheduledTransaction] = Field(default_factory=list)
