from collections.abc import Sequence
from enum import Enum
from typing import Optional, Self
from datetime import datetime, date, timedelta, time

from pydantic import BaseModel, Field
from tabulate import tabulate

from ..utils.format_money import format_money
from .actual import ScheduledTransaction


class Freq(Enum):
    MONTHLY = "MONTHLY"


class Recurrence(BaseModel):
    bymonthday: Optional[int] = None
    interval: int = 1
    dtstart: Optional[datetime] = None

    def get_occurrences(self, t: Optional[date] = None, until: Optional[date] = None):
        from dateutil.rrule import rrule, MONTHLY

        if t is None:
            t = date.today() + timedelta(days=1)

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
        cls, transactions: list[Self], start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        return sorted(
            (
                (txn_date, txn)
                for txn in transactions
                for txn_date in txn.recurrence.get_occurrences(start_date, end_date)
            ),
            key=lambda x: x[0],
        )

    @classmethod
    def cum_balance(
        cls,
        recurring_transactions: list[Self],
        scheduled_transactions: list[ScheduledTransaction],
        starting_cents: int = 0,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list["CumBalanceRow"]:
        # NOTE: the copy is just to appease the type checker
        transactions: Sequence[tuple[date, RecurringTransaction | ScheduledTransaction]] = list(
            cls.get_occurrences(recurring_transactions, start_date, end_date)
        )

        matched_scheduled_transactions = set()

        # if there is a scheduled transaction in the same month as a recurring transaction,
        # with the same description, replace the recurring transaction with the scheduled transaction
        # this is to allow for manual adjustments to recurring transactions
        # (e.g. if the recurring transaction is for a fixed amount, but the actual amount varies)
        for i, (txn_date, txn) in enumerate(transactions):
            for scheduled_txn in scheduled_transactions:
                if (
                    scheduled_txn.date.year == txn_date.year
                    and scheduled_txn.date.month == txn_date.month
                    and scheduled_txn.description == txn.description
                ):
                    transactions[i] = (txn_date, scheduled_txn)
                    matched_scheduled_transactions.add(scheduled_txn)
                    break

        # add any scheduled transactions that didn't match
        for scheduled_txn in scheduled_transactions:
            if scheduled_txn not in matched_scheduled_transactions:
                transactions.append((scheduled_txn.date, scheduled_txn))

        result = []

        total = starting_cents
        for txn_date, txn in transactions:
            total += txn.cents
            result.append(CumBalanceRow(date=txn_date, transaction=txn, balance_cents=total))

        return result


class CumBalanceRow(BaseModel):
    date: date
    transaction: RecurringTransaction | ScheduledTransaction
    balance_cents: int

    @classmethod
    def tabulate(cls, rows: Sequence[Self]):
        return tabulate(
            [
                (
                    row.date,
                    row.transaction.description,
                    format_money(row.transaction.cents),
                    format_money(row.balance_cents),
                )
                for row in rows
            ],
            headers=["Date", "Description", "Change", "Total"],
            colalign=("left", "left", "right", "right"),
        )
