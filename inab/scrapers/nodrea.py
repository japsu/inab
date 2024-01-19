"""
Parses the clipboard output of browser-console-scripts/nordea-credit-scrape.js pasted into the browser console.
"""

import re
import json
from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    PURCHASE = "Osto"
    RETURN = "Hyvitys"
    REPAYMENT = "Suoritus"
    UNKNOWN = "Tuntematon"


# note the minus here is a funky Unicode character, not - or –
SUM_REGEX = re.compile(r"^(?P<minus>−)?(?P<euros>\d+),(?P<cents>\d{2})$", re.UNICODE)


class CreditCardTransactionFromBrowserScript(BaseModel):
    date_fi: str = Field(alias="date")
    title: str
    amount: str

    class Config:
        frozen = True
        by_alias = True

    @property
    def date(self):
        return datetime.strptime(self.date_fi, "%d.%m.%Y").date()

    @property
    def cents(self):
        match = SUM_REGEX.match(self.amount)
        if not match:
            raise ValueError(f"Could not parse amount: {self.amount}")

        cents = 100 * int(match.group("euros")) + int(match.group("cents"))
        if match.group("minus"):
            cents = -cents

        return cents

    @property
    def type(self):
        type_fi, _ = self.title.split(" ", 1)
        return TransactionType(type_fi) if type_fi in TransactionType.__members__ else TransactionType.UNKNOWN

    @property
    def description(self):
        try:
            _, description = self.title.split(" ", 1)
            return description
        except ValueError:
            return self.title


class CreditCardTransaction(BaseModel):
    date: date
    description: str
    cents: int

    @classmethod
    def from_browser_script(cls, data: list[dict[str, Any]]):
        for txn in data:
            validated = CreditCardTransactionFromBrowserScript.model_validate(txn)
            yield cls(
                date=validated.date,
                description=validated.description,
                cents=validated.cents,
            )


if __name__ == "__main__":
    with open("data/credit_card_scrape.json", encoding="UTF-8") as input_file:
        for txn in CreditCardTransaction.from_browser_script(json.load(input_file)):
            print(txn)
