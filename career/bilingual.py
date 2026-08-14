from __future__ import annotations

OUTPUT_LANGUAGE_OPTIONS = [
    "Both / Beide",
    "English",
    "Deutsch",
]

def normalize_output_language(value: str) -> str:
    value = (value or "").strip()
    return value if value in OUTPUT_LANGUAGE_OPTIONS else "Both / Beide"

def split_items(value: str) -> list[str]:
    if not value:
        return []
    normalized = value.replace(";", "\n").replace(",", "\n")
    result = []
    seen = set()
    for part in normalized.splitlines():
        item = part.strip()
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result

def join_items(values: list[str]) -> str:
    return "\n".join(
        value.strip()
        for value in values or []
        if value.strip()
    )
