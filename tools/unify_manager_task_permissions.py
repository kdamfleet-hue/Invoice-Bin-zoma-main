#!/usr/bin/env python3
"""Unify manager-task authorization in the sidebar and page route.

Safe to run repeatedly. It edits only the two authorization blocks and fails
closed if the expected source text is not found, preventing accidental edits.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIDEBAR = ROOT / "templates/base.html"
ROUTE = ROOT / "routes/manager_tasks.py"

old_sidebar = """{% set sidebar_role = session.get('role') or session.get('user_role') or (session.get('google_user') or {}).get('role') %}
{% if is_admin or sidebar_role in ['admin','branch_manager','operations'] %}"""
new_sidebar = """{% set sidebar_user = session.get('user') or session.get('google_user') or {} %}
{% set sidebar_role = (session.get('role') or session.get('user_role') or sidebar_user.get('role') or '')|trim|lower %}
{% if is_admin or sidebar_role in ['admin','branch_manager','operations'] %}"""

old_route = """    if isinstance(user, dict) and str(user.get(\"role\") or \"\").lower() in MANAGER_ROLES:
        return True"""
new_route = """    if isinstance(user, dict) and str(user.get(\"role\") or \"\").strip().lower() in MANAGER_ROLES:
        return True"""


def replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        if new in text:
            return False
        raise SystemExit(f"Expected authorization block not found: {path}")
    if count != 1:
        raise SystemExit(f"Expected exactly one authorization block in {path}, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    return True


changed_sidebar = replace_once(SIDEBAR, old_sidebar, new_sidebar)
changed_route = replace_once(ROUTE, old_route, new_route)
print(f"sidebar_changed={changed_sidebar}")
print(f"route_changed={changed_route}")
print("✅ manager-task authorization blocks are aligned")
