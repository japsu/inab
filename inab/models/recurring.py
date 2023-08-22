from enum import Enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class Freq(Enum):
    MONTHLY = "MONTHLY"


class Recurrence(BaseModel):
    freq: Freq = Freq.MONTHLY
    bymonthday: Optional[int] = None
    interval: int = 1
    dtstart: Optional[datetime] = None

    def as_rrule(self):
        from dateutil.rrule import rrule, MONTHLY

        # TODO
        assert self.freq == Freq.MONTHLY

        return rrule(
            freq=MONTHLY,
            interval=self.interval,
            dtstart=self.dtstart,
            bymonthday=self.bymonthday,
        )


class RecurringTransaction(BaseModel):
    cents: int
    description: str
    other_party: str
    recurrence: Recurrence


if __name__ == "__main__":
    import yaml

    with open("data/recurring.yaml") as f:
        data = yaml.safe_load(f)

    for txn in [RecurringTransaction.model_validate(recurrence) for recurrence in data]:
        print(txn)
