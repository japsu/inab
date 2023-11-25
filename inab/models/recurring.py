from typing import Optional, Self
from datetime import datetime, date as date_type, timedelta, time

from pydantic import BaseModel, Field


class Recurrence(BaseModel):
    bymonthday: Optional[int] = None
    interval: int = 1
    dtstart: Optional[datetime] = None

    def get_occurrences(self, t: Optional[date_type] = None, until: Optional[date_type] = None):
        from dateutil.rrule import rrule, MONTHLY

        if t is None:
            t = date_type.today() + timedelta(days=1)

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
        cls,
        transactions: list[Self],
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
    ):
        return sorted(
            (
                (txn_date, txn)
                for txn in transactions
                for txn_date in txn.recurrence.get_occurrences(start_date, end_date)
            ),
            key=lambda x: x[0],
        )
