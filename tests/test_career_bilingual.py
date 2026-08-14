from career.bilingual import (
    join_items,
    normalize_output_language,
    split_items,
)

def test_split_items_supports_multiple_separators():
    assert split_items("Python, SQL; GCP\nSpark") == [
        "Python", "SQL", "GCP", "Spark"
    ]

def test_split_items_removes_case_insensitive_duplicates():
    assert split_items("Python\npython\nSQL\nsql") == [
        "Python", "SQL"
    ]

def test_join_items_uses_one_item_per_line():
    assert join_items(
        ["Data Engineer", "Cloud Data Engineer"]
    ) == "Data Engineer\nCloud Data Engineer"

def test_unknown_language_defaults_to_both():
    assert normalize_output_language("Unknown") == "Both / Beide"
