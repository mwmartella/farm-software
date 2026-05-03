def normalise_code_upper(v: str) -> str:
    if v is not None:
        return v.strip().upper()
    return v