from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .core import (
    ALLOWED_CHECKS, AgentError, apply_patch, dependency_levels, diff_paths,
    inspect_project, is_sensitive_path, prepare_worktree, read_context,
    restore_files, run_checks, scan_destructive_migrations, scan_secrets,
    snapshot_files, write_memory,
)


class EngineeringOrchestrator:
    def __init__(self, root: Path, provider: Any, max_attempts: int = 3, allow_sensitive: bool = False):
        self.root = root.resolve()
        self.provider = provider
        self.max_attempts = max(1, min(int(max_attempts), 3))
        self.allow_sensitive = allow_sensitive

    def inspect(self) -> dict[str, Any]:
        return {
            "project": inspect_project(self.root),
            "security_findings": scan_secrets(self.root),
            "database_findings": scan_destructive_migrations(self.root),
        }

    def run(self, objective: str) -> dict[str, Any]:
        if not objective.strip():
            raise AgentError("أدخل هدفًا هندسيًا واضحًا")
        branch = prepare_worktree(self.root)
        report = self.inspect()
        plan = self.provider.plan(objective, report["project"])
        tasks = plan.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            raise AgentError("الخطة لا تتضمن مهامًا قابلة للتحقق")
        if any(not isinstance(task, dict) or not isinstance(task.get("files", []), list)
               or not all(isinstance(item, str) for item in task.get("files", [])) for task in tasks):
            raise AgentError("شكل مهام الخطة غير صالح")
        levels = dependency_levels(tasks)
        planned = sorted({str(p) for task in tasks for p in task.get("files", [])})
        if not planned:
            raise AgentError("الخطة لم تحدد ملفات مستهدفة")
        for rel in planned:
            if is_sensitive_path(rel) and not self.allow_sensitive:
                raise AgentError(f"الخطة تمس ملفًا حساسًا ويتطلب --allow-sensitive: {rel}")
        checks = plan.get("checks", ["compile", "unit", "security", "migrations"])
        if not isinstance(checks, list) or set(checks) - ALLOWED_CHECKS:
            raise AgentError("الخطة طلبت فحصًا خارج القائمة المسموحة")
        context = read_context(self.root, planned, self.allow_sensitive)
        feedback = ""
        for attempt in range(1, self.max_attempts + 1):
            patch = self.provider.patch(objective, plan, context, feedback)
            changed = diff_paths(patch)
            if not set(changed).issubset(set(planned)):
                raise AgentError("الـ patch يغير ملفًا خارج الخطة")
            for rel in changed:
                if is_sensitive_path(rel) and not self.allow_sensitive:
                    raise AgentError(f"الـ patch يمس ملفًا حساسًا ويتطلب --allow-sensitive: {rel}")
            if scan_destructive_migrations(self.root, changed):
                raise AgentError("رُفض patch يتضمن عملية قاعدة بيانات مدمرة")
            snapshot = snapshot_files(self.root, changed, self.allow_sensitive)
            try:
                apply_patch(self.root, patch)
                results = run_checks(self.root, checks, changed)
            except Exception:
                restore_files(self.root, snapshot)
                raise
            failed = [r for r in results if r["status"] != "passed"]
            if not failed:
                write_memory(self.root, objective, "verified", branch, changed, results)
                return {"status": "verified", "branch": branch, "attempts": attempt,
                        "files": changed, "task_levels": levels, "checks": results,
                        "model": plan.get("_model", "configured")}
            restore_files(self.root, snapshot)
            feedback = "\n".join(
                f"{r['name']} ({r['status']}): {r.get('output', r.get('findings', r.get('note', '')))}"
                for r in failed
            )[:8000]
        write_memory(self.root, objective, "rolled-back", branch, planned, results)
        return {"status": "rolled-back", "branch": branch, "attempts": self.max_attempts,
                "files": planned, "task_levels": levels, "checks": results,
                "reason": "فشلت الفحوص بعد المحاولات المحدودة؛ أُعيدت الملفات إلى checkpoint."}
