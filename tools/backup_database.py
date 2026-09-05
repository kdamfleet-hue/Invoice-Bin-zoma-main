#!/usr/bin/env python3
"""Create a timestamped database backup without modifying operational data.

For PostgreSQL, set DATABASE_URL and ensure pg_dump is available.
For SQLite, set DATABASE_URL to sqlite:///path/to/database.db.
"""
from __future__ import annotations
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

url = os.environ.get("DATABASE_URL", "").strip()
backup_dir = Path(os.environ.get("BACKUP_DIR", "./backups")).expanduser()
backup_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

if not url:
    raise SystemExit("DATABASE_URL is required")
if url.startswith("sqlite:///"):
    source = Path(url.removeprefix("sqlite:///"))
    if not source.exists():
        raise SystemExit(f"SQLite database not found: {source}")
    target = backup_dir / f"database-{stamp}.sqlite3"
    shutil.copy2(source, target)
    print(target)
elif url.startswith(("postgres://", "postgresql://")):
    target = backup_dir / f"database-{stamp}.dump"
    result = subprocess.run(["pg_dump", "--format=custom", "--no-owner", "--file", str(target), url], check=False)
    if result.returncode:
        target.unlink(missing_ok=True)
        raise SystemExit(result.returncode)
    print(target)
else:
    raise SystemExit("Unsupported DATABASE_URL scheme; use sqlite:/// or postgresql://")
