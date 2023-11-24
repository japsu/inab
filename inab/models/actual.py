from datetime import date

from pydantic import BaseModel, Field


class ScheduledTransaction(BaseModel):
    date: date
    cents: int
    description: str


class Actual(BaseModel):
    account_balance_cents: int
    scheduled_transactions: list[ScheduledTransaction] = Field(default_factory=list)
