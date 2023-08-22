from pydantic import BaseModel


class RecurringTransaction(BaseModel):
    cents: int
    description: str
    other_party: str
