from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .core import AgentError
from .orchestrator import EngineeringOrchestrator
from .provider import GeminiProvider


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="وكيل هندسي محلي محمي لمشروع Bin Zomah")
    parser.add_argument("--root", default=".", help="جذر المستودع")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("inspect", help="إنشاء خريطة المشروع وفحوص أسرار/مهاجرات للقراءة فقط")
    run = sub.add_parser("run", help="خطة ثم patch واختبارات مع تراجع تلقائي عند الفشل")
    run.add_argument("--task", required=True, help="هدف هندسي واحد")
    run.add_argument("--max-attempts", type=int, default=3, choices=(1, 2, 3))
    run.add_argument("--allow-sensitive", action="store_true", help="السماح بملفات حساسة لهذا التشغيل فقط")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "inspect":
            orchestrator = EngineeringOrchestrator(root, provider=None)
            result = orchestrator.inspect()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            high_severity = any(f.get("severity") == "high" for f in result["security_findings"])
            return 0 if not high_severity and not result["database_findings"] else 2
        provider = GeminiProvider()
        orchestrator = EngineeringOrchestrator(root, provider, args.max_attempts, args.allow_sensitive)
        result = orchestrator.run(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "verified" else 1
    except AgentError as exc:
        print(f"Agent stopped safely: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        # Do not print tracebacks by default; provider/runtime details may contain sensitive data.
        print(f"Agent failed safely: {type(exc).__name__}", file=sys.stderr)
        return 3
