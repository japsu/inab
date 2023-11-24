from enum import Enum
from typing import Optional, Self
from datetime import datetime, date, timedelta, time

from pydantic import BaseModel, Field
from tabulate import tabulate

from ..utils.format_money import format_money


class Freq(Enum):
    MONTHLY = "MONTHLY"


class Recurrence(BaseModel):
    freq: Freq = Freq.MONTHLY
    bymonthday: Optional[int] = None
    interval: int = 1
    dtstart: Optional[datetime] = None

    def get_occurrences(self, t: Optional[date] = None, until: Optional[date] = None):
        from dateutil.rrule import rrule, MONTHLY

        assert self.freq == Freq.MONTHLY

        if t is None:
            t = date.today()

        if until is None:
            until = t + timedelta(days=120)

        return [
            dt.date()
            for dt in rrule(
                freq=MONTHLY,
                interval=self.interval,
                dtstart=self.dtstart,
                bymonthday=self.bymonthday,
                until=datetime.combine(until, time(0)),
            )
            if dt.date() >= t and dt.date() <= until
        ]


class RecurringTransaction(BaseModel):
    cents: int
    description: str
    other_party: str
    recurrence: Recurrence = Field(repr=False)

    @classmethod
    def get_occurrences(
        cls, transactions: list[Self], t: Optional[date] = None, until: Optional[date] = None
    ):
        return sorted(
            (
                (recurrence, txn)
                for txn in transactions
                for recurrence in txn.recurrence.get_occurrences(t, until)
            ),
            key=lambda x: x[0],
        )

    @classmethod
    def cum_balance(
        cls,
        transactions: list[Self],
        starting_cents: int = 0,
        t: Optional[date] = None,
        until: Optional[date] = None,
    ):
        total = starting_cents
        for txn_date, txn in cls.get_occurrences(transactions, t, until):
            total += txn.cents
            yield txn_date, total, txn
