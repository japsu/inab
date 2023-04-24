import re
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class TransactionType(str, Enum):
    PURCHASE = "Osto"
    RETURN = "Hyvitys"
    REPAYMENT = "Suoritus"
    UNKNOWN = "Tuntematon"


class State(str, Enum):
    DATE = r"^(?P<date>\d{1,2}\.\d{1,2}\.\d{4})$"
    DESCRIPTION = r"^(?P<type>Osto|Suoritus|Hyvitys) (?P<description>.+)"
    SUM = r"^(?P<minus>−)?(?P<euros>\d+),(?P<cents>\d{2})$"


class CreditCardTransaction(BaseModel):
    type: TransactionType
    date: date
    description: str
    cents: int

    @classmethod
    def from_nodrea(cls, lines):
        state = State.DATE
        date_ = date(1970, 1, 1)
        type = TransactionType.UNKNOWN
        description = ""

        for line in lines:
            if match := re.match(state.value, line, re.UNICODE):
                match state:
                    case State.DATE:
                        date_ = datetime.strptime(match.group("date"), "%d.%m.%Y").date()
                        state = State.DESCRIPTION

                    case State.DESCRIPTION:
                        type = TransactionType(match.group("type"))
                        description = match.group("description")
                        state = State.SUM

                    case State.SUM:
                        cents = 100 * int(match.group("euros")) + int(match.group("cents"))
                        if match.group("minus"):
                            cents = -cents

                        yield cls(type=type, date=date_, description=description, cents=cents)

                        state = State.DATE
                        date_ = date(1970, 1, 1)
                        type = TransactionType.UNKNOWN
                        description = ""

                    case _:
                        raise NotImplementedError(state)


if __name__ == "__main__":
    from sys import stdin

    for txn in CreditCardTransaction.from_nodrea(stdin.readlines()):
        print(txn)
