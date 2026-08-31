import os
import logging
import pandas as pd
from functools import lru_cache

logger = logging.getLogger("InvoiceApp")

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_FILENAME = "جدول_بيانات_السائقين_والمركبات_المدمج_كامل.xlsx"


def _excel_candidates():
    env_path = (os.environ.get("BIRTH_MAPPING_XLSX") or "").strip()
    return [
        p for p in [
            env_path,
            os.path.join(_ROOT, _FILENAME),
            os.path.join("/app", _FILENAME),
            os.path.join("/persist", _FILENAME),
            os.path.join("/data", _FILENAME),
        ] if p
    ]


@lru_cache(maxsize=1)
def load_birth_mapping():
    """Load optional employee-id → birth-date map. Missing file is not an error."""
    excel_path = next((p for p in _excel_candidates() if os.path.isfile(p)), None)
    if not excel_path:
        logger.info("birth_mapping: optional Excel not present — birth_date enrichment disabled.")
        return {}
    df = pd.read_excel(excel_path)
    emp_col = None
    birth_col = None
    for col in df.columns:
        col_low = str(col).lower()
        if any(kw in col_low for kw in ["رقم وظيف", "employee id", "emp_id", "id"]):
            emp_col = col
        if any(kw in col_low for kw in ["تاريخ ميلاد", "birth date", "date of birth", "dob"]):
            birth_col = col
    if emp_col is None or birth_col is None:
        logger.info("birth_mapping: employee ID or birth date columns not found — enrichment disabled.")
        return {}
    mapping = {}
    for _, row in df.iterrows():
        emp_id = str(row[emp_col]).strip()
        birth = row[birth_col]
        if pd.isna(birth):
            continue
        if isinstance(birth, pd.Timestamp):
            birth_str = birth.date().isoformat()
        else:
            birth_str = str(birth).strip()
        mapping[emp_id] = birth_str
    return mapping
