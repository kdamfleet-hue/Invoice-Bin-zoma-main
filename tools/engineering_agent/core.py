from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXCLUDED_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__", "instance", "uploads", ".agent-memory"}
TEXT_SUFFIXES = {".py", ".md", ".html", ".js", ".css", ".json", ".yml", ".yaml", ".toml", ".ini", ".txt", ".sql", ".sh"}
SECRET_NAME = re.compile(r"(?i)(^|/)(\.env(?:\..*)?|.*secret.*|.*credential.*|cookies.*\.txt|headers\.txt)$")
SECRET_VALUE = re.compile(r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*(['\"])(?!\$|<|your_|change_me|example|xxx)[^'\"\n]{24,}\1")
KEY_VALUE = re.compile(r"(?:AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9]{24,})")
DESTRUCTIVE_SQL = re.compile(r"(?i)\b(?:DROP\s+(?:TABLE|DATABASE|COLUMN)\b|TRUNCATE\b|DELETE\s+FROM\s+\w+\s*;)")
SENSITIVE_PARTS = {".github", "migrations", "models", "secrets", "credentials", "auth", "security"}
SENSITIVE_ROOTS = {"app.py", "Dockerfile", "start.sh"}
ALLOWED_CHECKS = {"unit", "compile", "security", "migrations", "performance"}


class AgentError(RuntimeError):
    pass


def choose_model(complexity: int, risk: str, context_chars: int, accuracy: float, fast: str, reasoning: str) -> str:
    """Deterministic cost/latency/accuracy routing; values are configurable by environment."""
    use_reasoning = (
        complexity >= 4 or risk.lower() in {"high", "critical"}
        or accuracy >= 0.9 or context_chars >= 24000
    )
    return reasoning if use_reasoning else fast


def dependency_levels(tasks: list[dict[str, Any]]) -> list[list[str]]:
    ids = [str(t.get("id", "")).strip() for t in tasks]
    if any(not i for i in ids) or len(set(ids)) != len(ids):
        raise AgentError("خطة المهام تحتوي معرفات فارغة أو مكررة")
    remaining = {str(t["id"]): set(map(str, t.get("depends_on", []))) for t in tasks}
    if any(dep not in remaining for deps in remaining.values() for dep in deps):
        raise AgentError("الخطة تشير إلى اعتماد غير موجود")
    levels: list[list[str]] = []
    completed: set[str] = set()
    while remaining:
        ready = sorted(k for k, deps in remaining.items() if deps <= completed)
        if not ready:
            raise AgentError("اكتُشفت دورة في اعتماديات الخطة")
        levels.append(ready)
        completed.update(ready)
        for key in ready:
            remaining.pop(key)
    return levels


def is_sensitive_path(rel: str) -> bool:
    p = Path(rel)
    normalized = rel.replace("\\", "/").lower()
    return (
        p.name in SENSITIVE_ROOTS or any(token in part.lower() for part in p.parts for token in SENSITIVE_PARTS)
        or SECRET_NAME.search(normalized) is not None
        or p.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".pem", ".key"}
        or p.name.lower().startswith("requirements")
        or "production" in normalized or "deploy" in normalized
    )


def resolve_safe(root: Path, raw: str, allow_sensitive: bool = False) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise AgentError("مسار ملف فارغ")
    rel = Path(raw)
    if rel.is_absolute() or ".." in rel.parts:
        raise AgentError(f"مسار غير آمن: {raw}")
    root = root.resolve()
    candidate = root / rel
    # Reject symlinks, even if their current target remains inside the repository.
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise AgentError(f"المسارات الرمزية غير مسموحة: {raw}")
    resolved = candidate.resolve()
    if root != resolved and root not in resolved.parents:
        raise AgentError(f"المسار يخرج عن مجلد المشروع: {raw}")
    if is_sensitive_path(rel.as_posix()) and not allow_sensitive:
        raise AgentError(f"الملف حساس ويتطلب --allow-sensitive: {raw}")
    if candidate.suffix.lower() not in TEXT_SUFFIXES:
        raise AgentError(f"نوع الملف غير مسموح للوكيل: {raw}")
    return candidate


def _walk_files(root: Path):
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS and (not d.startswith(".") or d == ".github"))
        for name in sorted(files):
            path = Path(current) / name
            rel = path.relative_to(root).as_posix()
            if path.suffix.lower() in TEXT_SUFFIXES and not SECRET_NAME.search(rel):
                yield path, rel


def inspect_project(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files: list[dict[str, Any]] = []
    routes: list[str] = []
    modules: set[str] = set()
    tests: list[str] = []
    dependencies: list[str] = []
    route_re = re.compile(r"@\w+\.route\([\"']([^\"']+)")
    for path, rel in _walk_files(root):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        files.append({"path": rel, "bytes": size})
        if rel.startswith("routes/") or rel.startswith("services/") or rel.startswith("models/"):
            modules.add(rel.split("/", 1)[0])
        if rel.startswith("tests/") or Path(rel).name.startswith("test_"):
            tests.append(rel)
        if rel.startswith("requirements") and path.name.endswith(".txt"):
            try:
                dependencies.extend(line.strip() for line in path.read_text(errors="ignore").splitlines()
                                   if line.strip() and not line.lstrip().startswith(("#", "-")))
            except OSError:
                pass
        if path.suffix == ".py" and rel.startswith("routes/"):
            try:
                routes.extend(f"{rel}:{route}" for route in route_re.findall(path.read_text(errors="ignore")))
            except OSError:
                pass
    return {
        "root": root.name,
        "file_count": len(files),
        "files": files[:1500],
        "modules": sorted(modules),
        "routes": sorted(set(routes))[:500],
        "tests": sorted(tests),
        "dependencies": sorted(set(dependencies)),
        "migration_files": [f["path"] for f in files if "migration" in f["path"].lower() or f["path"].startswith("migrations/")],
        "ci_files": [f["path"] for f in files if f["path"].startswith((".github/workflows/", ".gitlab-ci"))],
    }


def scan_secrets(root: Path, paths: list[str] | None = None) -> list[dict[str, Any]]:
    root = root.resolve()
    candidates = []
    if paths is None:
        candidates = list(_walk_files(root))
    else:
        for rel in paths:
            path = resolve_safe(root, rel, allow_sensitive=True)
            candidates.append((path, rel))
    findings = []
    for path, rel in candidates:
        if path.name == ".env.example" or path.stat().st_size > 500_000:
            continue
        try:
            for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
                if SECRET_VALUE.search(line) or KEY_VALUE.search(line):
                    findings.append({"path": rel, "line": number, "type": "possible-hardcoded-secret",
                                     "severity": "warning" if rel.startswith(("tests/", "test_")) else "high"})
        except (OSError, UnicodeError):
            continue
    return findings


def scan_destructive_migrations(root: Path, paths: list[str] | None = None) -> list[dict[str, Any]]:
    root = root.resolve()
    if paths is None:
        candidates = [(p, r) for p, r in _walk_files(root)
                      if r.startswith("migrations/") or p.suffix.lower() == ".sql"]
    else:
        candidates = []
        for rel in paths:
            if "migration" not in rel.lower() and Path(rel).suffix.lower() != ".sql":
                continue
            candidates.append((resolve_safe(root, rel, allow_sensitive=True), rel))
    findings = []
    for path, rel in candidates:
        try:
            for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
                if DESTRUCTIVE_SQL.search(line):
                    findings.append({"path": rel, "line": number, "type": "destructive-database-operation"})
        except (OSError, UnicodeError):
            pass
    return findings


def git_branch(root: Path) -> str:
    result = subprocess.run(["git", "branch", "--show-current"], cwd=root, text=True,
                            capture_output=True, check=True, timeout=10)
    return result.stdout.strip()


def prepare_worktree(root: Path) -> str:
    status = subprocess.run(["git", "status", "--porcelain"], cwd=root, text=True,
                            capture_output=True, check=True, timeout=10)
    if status.stdout.strip():
        raise AgentError("أوقف التنفيذ: مجلد العمل غير نظيف؛ احفظ تعديلاتك أو انقلها قبل تشغيل الوكيل")
    branch = git_branch(root)
    if branch in {"main", "master"}:
        name = "engineering-agent/" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        subprocess.run(["git", "switch", "-c", name], cwd=root, check=True, timeout=10,
                       capture_output=True, text=True)
        branch = name
    return branch


def diff_paths(patch: str) -> list[str]:
    if not patch.strip() or len(patch) > 250_000:
        raise AgentError("التغيير فارغ أو يتجاوز الحد الأقصى 250KB")
    if ("GIT binary patch" in patch or "rename from " in patch or "deleted file mode" in patch
            or "new file mode 120000" in patch or "old mode " in patch or "new mode " in patch):
        raise AgentError("تغييرات الملفات الثنائية أو الحذف أو إعادة التسمية ممنوعة")
    result = []
    for line in patch.splitlines():
        if line.startswith("+++ "):
            value = line[4:].strip()
            if value == "/dev/null" or not value.startswith("b/"):
                raise AgentError("يُسمح بتعديل/إضافة ملفات نصية فقط؛ الحذف مرفوض")
            result.append(value[2:])
    paths = sorted(set(result))
    if not paths:
        raise AgentError("لم يعثر الوكيل على ملفات معدلة في الـ patch")
    return paths


def snapshot_files(root: Path, paths: list[str], allow_sensitive: bool) -> dict[str, bytes | None]:
    snapshot = {}
    for rel in paths:
        path = resolve_safe(root, rel, allow_sensitive)
        if path.exists() and not path.is_file():
            raise AgentError(f"ليس ملفًا عاديًا: {rel}")
        snapshot[rel] = path.read_bytes() if path.exists() else None
    return snapshot


def apply_patch(root: Path, patch: str) -> None:
    check = subprocess.run(["git", "apply", "--check", "-"], cwd=root, input=patch,
                           text=True, capture_output=True, timeout=20)
    if check.returncode:
        raise AgentError("تعذر التحقق من patch: " + (check.stderr.strip() or "تعارض في السياق"))
    applied = subprocess.run(["git", "apply", "-"], cwd=root, input=patch,
                             text=True, capture_output=True, timeout=20)
    if applied.returncode:
        raise AgentError("تعذر تطبيق patch: " + (applied.stderr.strip() or "خطأ Git"))


def restore_files(root: Path, snapshot: dict[str, bytes | None]) -> None:
    for rel, content in snapshot.items():
        path = (root / rel).resolve()
        if root.resolve() != path and root.resolve() not in path.parents:
            raise AgentError("رفض التراجع عن مسار خارج المشروع")
        if content is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)


def _safe_env() -> dict[str, str]:
    # Tests must not inherit production database, mail, or AI credentials.
    blocked = re.compile(r"(?i)(secret|password|token|api.?key|database.?url|smtp|mail_|gemini|openai|aws_|azure_)")
    env = {k: v for k, v in os.environ.items() if not blocked.search(k)}
    env.update({"ALLOW_SQLITE_FALLBACK": "true", "SECRET_KEY": "local-engineering-agent-test"})
    return env


def run_check(root: Path, name: str, paths: list[str] | None = None, timeout: int = 300) -> dict[str, Any]:
    started = time.perf_counter()
    if name == "security":
        findings = scan_secrets(root, paths)
        result = {"status": "failed" if any(f.get("severity") == "high" for f in findings) else "passed", "findings": findings}
    elif name == "migrations":
        findings = scan_destructive_migrations(root, paths)
        result = {"status": "failed" if findings else "passed", "findings": findings}
    elif name == "performance":
        result = {"status": "passed", "note": "زمن الفحوص يسجل كمؤشر؛ لا يوجد benchmark خاص بالتطبيق مُهيأ بعد"}
    else:
        commands = {
            "compile": [sys.executable, "-m", "compileall", "-q", "app.py", "routes", "services", "tools"],
            "unit": ([sys.executable, "-m", "pytest", "-q"] if _pytest_available()
                     else [sys.executable, "-m", "unittest", "discover", "-s", "tests"]),
        }
        if name not in commands:
            raise AgentError(f"فحص غير مسموح: {name}")
        proc = subprocess.run(commands[name], cwd=root, env=_safe_env(), text=True,
                              capture_output=True, timeout=timeout)
        output = (proc.stdout + "\n" + proc.stderr)[-8000:]
        result = {"status": "passed" if proc.returncode == 0 else "failed",
                  "exit_code": proc.returncode, "output": output}
    result["name"] = name
    result["seconds"] = round(time.perf_counter() - started, 3)
    return result


def _pytest_available() -> bool:
    try:
        import importlib.util
        return importlib.util.find_spec("pytest") is not None
    except (ImportError, ValueError):
        return False


def run_checks(root: Path, names: list[str], paths: list[str]) -> list[dict[str, Any]]:
    selected = sorted(set(names))
    if not selected:
        selected = ["compile", "unit", "security", "migrations"]
    unknown = set(selected) - ALLOWED_CHECKS
    if unknown:
        raise AgentError("فحوص غير مسموحة: " + ", ".join(sorted(unknown)))
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(4, len(selected) or 1)) as pool:
        futures = {pool.submit(run_check, root, name, paths): name for name in selected}
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda r: r["name"])


def read_context(root: Path, paths: list[str], allow_sensitive: bool, max_chars: int = 80000) -> dict[str, str]:
    context: dict[str, str] = {}
    used = 0
    for rel in paths:
        path = resolve_safe(root, rel, allow_sensitive)
        if not path.exists():
            continue
        if path.stat().st_size > 40000:
            raise AgentError(f"حجم ملف السياق أكبر من 40KB: {rel}")
        text = path.read_text(errors="strict")
        text = SECRET_VALUE.sub(lambda m: m.group(0).split("=")[0] + "=\"[REDACTED]\"", text)
        text = KEY_VALUE.sub("[REDACTED_KEY]", text)
        if used + len(text) > max_chars:
            raise AgentError("سياق الملفات يتجاوز الحد الآمن 80KB")
        context[rel] = text
        used += len(text)
    return context


def write_memory(root: Path, objective: str, status: str, branch: str,
                 paths: list[str], checks: list[dict[str, Any]]) -> None:
    memory_dir = root / ".agent-memory"
    memory_dir.mkdir(exist_ok=True)
    target = memory_dir / "history.json"
    try:
        history = json.loads(target.read_text()) if target.exists() else {"version": 1, "runs": []}
    except (OSError, ValueError):
        history = {"version": 1, "runs": []}
    history["runs"].append({
        "at": datetime.now(timezone.utc).isoformat(),
        "objective_sha256": hashlib.sha256(objective.encode()).hexdigest(),
        "status": status, "branch": branch, "files": paths,
        "checks": [{"name": c["name"], "status": c["status"], "seconds": c["seconds"]} for c in checks],
    })
    history["runs"] = history["runs"][-100:]
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(history, ensure_ascii=False, indent=2))
    tmp.replace(target)
