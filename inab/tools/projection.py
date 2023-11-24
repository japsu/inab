import yaml
from tabulate import tabulate

from ..models.actual import Actual
from ..models.recurring import RecurringTransaction, CumBalanceRow
from ..utils.format_money import format_money


def main():
    with open("data/actual.yaml") as f:
        data = yaml.safe_load(f)

    actual = Actual.model_validate(data)

    with open("data/recurring.yaml") as f:
        data = yaml.safe_load(f)

    recurring_transactions = [RecurringTransaction.model_validate(recurrence) for recurrence in data]
    cum_balance_rows = RecurringTransaction.cum_balance(
        recurring_transactions,
        scheduled_transactions=actual.scheduled_transactions,
        starting_cents=actual.account_balance_cents,
    )

    print(CumBalanceRow.tabulate(cum_balance_rows))


if __name__ == "__main__":
    main()
