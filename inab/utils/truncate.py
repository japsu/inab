def truncate(s: str, max_width: int, ellipsis: str = "…") -> str:
    if len(s) <= max_width:
        return s
    else:
        return s[: max_width - len(ellipsis)] + ellipsis
