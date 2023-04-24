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
    DATE_OR_DESCRIPTION = r"^((?P<date>\d{1,2}\.\d{1,2}\.\d{4})|(?P<type>Osto|Suoritus|Hyvitys) (?P<description>.+))$"
    SUM = r"^(?P<minus>−)?(?P<euros>\d+),(?P<cents>\d{2})$"


class CreditCardTransaction(BaseModel):
    type: TransactionType
    date: date
    description: str
    cents: int

    @classmethod
    def from_nodrea(cls, lines):
        state = State.DATE_OR_DESCRIPTION
        date_ = date(1970, 1, 1)
        type = TransactionType.UNKNOWN
        description = ""

        for line in lines:
            if match := re.match(state.value, line, re.UNICODE):
                match state:
                    case State.DATE_OR_DESCRIPTION:
                        if date_str := match.group("date"):
                            # there may be 1 to 3 dates, the last of which is the interesting one
                            date_ = datetime.strptime(match.group("date"), "%d.%m.%Y").date()
                        elif type_str := match.group("type"):
                            type = TransactionType(type_str)
                            description = match.group("description")
                            state = State.SUM

                    case State.SUM:
                        cents = 100 * int(match.group("euros")) + int(match.group("cents"))
                        if match.group("minus"):
                            cents = -cents

                        yield cls(type=type, date=date_, description=description, cents=cents)

                        state = State.DATE_OR_DESCRIPTION
                        date_ = date(1970, 1, 1)
                        type = TransactionType.UNKNOWN
                        description = ""

                    case _:
                        raise NotImplementedError(state)


if __name__ == "__main__":
    with open("examples/credit_card_copypasta.txt", encoding="UTF-8") as input_file:
        for txn in CreditCardTransaction.from_nodrea(input_file.readlines()):
            print(txn)
