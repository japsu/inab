from datetime import date

from pydantic import BaseModel, Field


class ScheduledTransaction(BaseModel):
    date: date
    cents: int
    description: str

    class Config:
        frozen = True


class Actual(BaseModel):
    date: date
    account_balance_cents: int
    scheduled_transactions: list[ScheduledTransaction] = Field(default_factory=list)
