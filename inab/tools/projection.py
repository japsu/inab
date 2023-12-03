from datetime import timedelta

import yaml

from ..models.actual import Actual
from ..models.recurring import RecurringTransaction
from ..models.cumulative_balance import CumulativeBalance


def main():
    with open("data/actual.yaml") as f:
        data = yaml.safe_load(f)

    actual = Actual.model_validate(data)

    with open("data/recurring.yaml") as f:
        data = yaml.safe_load(f)

    start_date = actual.date + timedelta(days=1)

    recurring_transactions = [RecurringTransaction.model_validate(recurrence) for recurrence in data]
    cumulative_balances = CumulativeBalance.calculate(
        recurring_transactions=recurring_transactions,
        scheduled_transactions=actual.scheduled_transactions,
        starting_cents=actual.account_balance_cents,
        start_date=start_date,
    )

    print(
        CumulativeBalance.tabulate(
            cumulative_balances,
            starting_cents=actual.account_balance_cents,
            start_date=start_date,
        )
    )


if __name__ == "__main__":
    main()
