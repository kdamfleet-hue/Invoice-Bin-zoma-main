import os
import logging
import pandas as pd
from functools import lru_cache

logger = logging.getLogger("InvoiceApp")

# Path to the merged drivers/vehicles Excel file (project root)
EXCEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'جدول_بيانات_السائقين_والمركبات_المدمج_كامل.xlsx')

@lru_cache(maxsize=1)
def load_birth_mapping():
    """Load the Excel file and return a dict mapping employee ID → birth date (YYYY-MM-DD).
    The result is cached for the lifetime of the process.

    This file is optional enrichment data, not something every deploy will have — if it's
    missing, callers (e.g. GET /api/drivers) must keep working with no birth_date field
    rather than 500 on every request, so this returns {} instead of raising.
    """
    if not os.path.exists(EXCEL_PATH):
        logger.warning(f"birth_mapping: Excel file not found at {EXCEL_PATH} — birth_date enrichment disabled.")
        return {}
    df = pd.read_excel(EXCEL_PATH)
    # Identify columns (allow slight variations in naming)
    emp_col = None
    birth_col = None
    for col in df.columns:
        col_low = str(col).lower()
        if any(kw in col_low for kw in ["رقم وظيف", "employee id", "emp_id", "id"]):
            emp_col = col
        if any(kw in col_low for kw in ["تاريخ ميلاد", "birth date", "date of birth", "dob"]):
            birth_col = col
    if emp_col is None or birth_col is None:
        logger.warning("birth_mapping: could not locate employee ID or birth date columns in Excel file — birth_date enrichment disabled.")
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
