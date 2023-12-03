from collections.abc import Sequence
from typing import Optional, Self
from datetime import date as date_type

from pydantic import BaseModel
from tabulate import tabulate

from ..utils.format_money import format_money
from .actual import ScheduledTransaction
from .recurring import RecurringTransaction


class CumulativeBalance(BaseModel):
    date: date_type
    transaction: RecurringTransaction | ScheduledTransaction
    balance_cents: int

    @classmethod
    def tabulate(
        cls,
        rows: Sequence[Self],
        starting_cents: Optional[int] = None,
        start_date: Optional[date_type] = None,
    ):
        tabular_data = [
            (
                row.date.isoformat(),
                row.transaction.description,
                format_money(row.transaction.cents),
                format_money(row.balance_cents),
            )
            for row in rows
        ]

        if starting_cents is not None:
            tabular_data.insert(
                0,
                (
                    start_date.isoformat() if start_date is not None else "",
                    "Starting Balance",
                    "",
                    format_money(starting_cents),
                ),
            )

        return tabulate(
            tabular_data,
            headers=["Date", "Description", "Change", "Total"],
            colalign=("left", "left", "right", "right"),
        )

    @classmethod
    def calculate(
        cls,
        recurring_transactions: list[RecurringTransaction],
        scheduled_transactions: list[ScheduledTransaction],
        start_date: date_type,
        starting_cents: int = 0,
        end_date: Optional[date_type] = None,
    ) -> list["CumulativeBalance"]:
        # NOTE: the copy is just to appease the type checker
        transactions: Sequence[tuple[date_type, RecurringTransaction | ScheduledTransaction]] = list(
            RecurringTransaction.get_occurrences(recurring_transactions, start_date, end_date)
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
                    transactions[i] = (scheduled_txn.date, scheduled_txn)
                    matched_scheduled_transactions.add(scheduled_txn)
                    break

        # add any scheduled transactions that didn't match
        for scheduled_txn in scheduled_transactions:
            if scheduled_txn not in matched_scheduled_transactions:
                transactions.append((scheduled_txn.date, scheduled_txn))

        # discard past transactions
        transactions = [txn for txn in transactions if txn[0] >= start_date]

        result = []

        total = starting_cents
        for txn_date, txn in transactions:
            total += txn.cents
            result.append(CumulativeBalance(date=txn_date, transaction=txn, balance_cents=total))

        return result
