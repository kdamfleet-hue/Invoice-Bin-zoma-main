#!/usr/bin/env python3
"""Measure public, read-only health/documentation endpoints without credentials."""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://invoice-bin-zoma.509.rip").rstrip("/")
ENDPOINTS = [
    ("health", "/health"),
    ("system_health", "/system_health"),
    ("system_metrics", "/api/system_metrics"),
    ("system_features", "/api/system_features"),
    ("api_docs", "/api/docs"),
    ("api_health", "/api/health"),
]

rows = []
for name, path in ENDPOINTS:
    samples = []
    statuses = []
    sizes = []
    for _ in range(3):
        start = time.perf_counter()
        proc = subprocess.run(
            ["curl", "-sS", "--max-time", "20", "-o", "/tmp/api_measure_body", "-w", "%{http_code}", f"{BASE}{path}"],
            capture_output=True,
            text=True,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        samples.append(elapsed_ms)
        statuses.append(proc.stdout.strip() or "000")
        try:
            sizes.append(Path("/tmp/api_measure_body").stat().st_size)
        except FileNotFoundError:
            sizes.append(0)
    rows.append({
        "name": name,
        "path": path,
        "status_codes": statuses,
        "min_ms": round(min(samples), 2),
        "median_ms": round(statistics.median(samples), 2),
        "max_ms": round(max(samples), 2),
        "body_bytes": sizes[-1],
    })

print(json.dumps({"base": BASE, "measured_at": datetime.now(timezone.utc).isoformat(), "samples_per_endpoint": 3, "endpoints": rows}, ensure_ascii=False, indent=2))
