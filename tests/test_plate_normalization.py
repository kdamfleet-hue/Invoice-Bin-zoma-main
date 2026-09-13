import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from helpers import normalize_plate


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, ""),
        ("", ""),
        ("ب ح ل ٤٤٣٥", "4435BJL"),
        ("ب-ح-ل-4435", "4435BJL"),
        ("BJL 4435", "4435BJL"),
        ("ب ح ل ۴۴۳۵", "4435BJL"),
        ("  ر ن ر / ٥٠٥٩ ", "5059RNR"),
        ("ر ن ر 5059", "5059RNR"),
    ],
)
def test_normalize_plate_forms_a_stable_key(raw, expected):
    assert normalize_plate(raw) == expected


def test_arabic_and_latin_plate_forms_match():
    assert normalize_plate("ب ح ل ٤٤٣٥") == normalize_plate("BJL-4435")


def test_display_value_is_not_modified_by_normalizer():
    raw = "ب ح ل ٤٤٣٥"
    normalized = normalize_plate(raw)
    assert raw == "ب ح ل ٤٤٣٥"
    assert normalized == "4435BJL"
