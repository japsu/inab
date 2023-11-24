def format_money(cents: int):
    """
    >>> format_money(338200)
    '3382,00 €'
    """
    return f"{cents / 100:.2f} €".replace(".", ",")
