import yaml
from tabulate import tabulate

from ..models.actual import Actual
from ..models.recurring import RecurringTransaction
from ..utils.format_money import format_money


def main():
    with open("data/actual.yaml") as f:
        data = yaml.safe_load(f)

    actual = Actual.model_validate(data)

    with open("data/recurring.yaml") as f:
        data = yaml.safe_load(f)

    recurring_transactions = [RecurringTransaction.model_validate(recurrence) for recurrence in data]

    print(
        tabulate(
            [
                (recurrence, txn.description, format_money(txn.cents), format_money(total_cents))
                for recurrence, total_cents, txn in RecurringTransaction.cum_balance(
                    recurring_transactions,
                    starting_cents=actual.account_balance_cents,
                )
            ],
            headers=["Date", "Description", "Change", "Total"],
            colalign=("right", "left", "right", "right"),
        )
    )


if __name__ == "__main__":
    main()
