def pt_to_float(value: str) -> float:
    """Convert a typst dimension like '7.2pt' to a float point value."""
    return float(value.replace("pt", ""))
