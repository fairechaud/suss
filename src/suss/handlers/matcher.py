def parse_csv(values: str | None) -> list[str]:
    if not values:
        return []
    return [v.strip() for v in values.split(",") if v.strip()]

def normalise(s: str, mode: str ="insensitive") -> str:
    return s.strip().lower() if mode == "insensitive" else s.strip()

def build_set(values: list[str], mode: str ="insensitive") -> set[str]:
    return {normalise(v, mode) for v in values}

def match_any(field_to_match: str, criteria: list[str], mode: str = "insensitive") -> bool:
    field_set = build_set(parse_csv(field_to_match), mode)
    criteria_set = build_set(criteria, mode)
    return bool(field_set & criteria_set)

def match_all(field_to_match: str, criteria: list[str], mode: str = "insensitive") -> bool:
    field_set = build_set(parse_csv(field_to_match), mode)
    criteria_set = build_set(criteria, mode)
    return criteria_set <= field_set
