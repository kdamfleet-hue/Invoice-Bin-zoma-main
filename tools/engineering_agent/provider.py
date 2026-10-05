from __future__ import annotations

import json
import os
import re
import time
from typing import Any

import requests

from .core import AgentError, choose_model


class GeminiProvider:
    """Opt-in developer-only LLM adapter. Never logs credentials or response secrets."""

    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key: str | None = None, fast_model: str | None = None,
                 reasoning_model: str | None = None, timeout: int = 90):
        self.api_key = (api_key if api_key is not None else os.environ.get("GEMINI_API_KEY", "")).strip()
        self.fast_model = fast_model or os.environ.get("ENGINEERING_FAST_MODEL", "gemini-2.5-flash")
        self.reasoning_model = reasoning_model or os.environ.get("ENGINEERING_REASONING_MODEL", "gemini-2.5-pro")
        self.timeout = timeout

    def _complete_json(self, system: str, prompt: str, model: str) -> dict[str, Any]:
        if not self.api_key:
            raise AgentError("GEMINI_API_KEY غير مضبوط؛ أوامر الفحص المحلية لا تحتاج مفتاحًا")
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192, "responseMimeType": "application/json"},
        }
        last_error = "تعذر الوصول إلى نموذج Gemini"
        for attempt in range(3):
            try:
                response = requests.post(self.URL.format(model=model),
                    headers={"X-goog-api-key": self.api_key, "Content-Type": "application/json"},
                    json=body, timeout=self.timeout)
            except requests.RequestException:
                last_error = "فشل اتصال Gemini"
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
                continue
            if response.status_code in (429, 503):
                last_error = f"Gemini مشغول (HTTP {response.status_code})"
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
                continue
            if response.status_code != 200:
                # Do not echo request headers or provider response bodies; they may contain sensitive data.
                raise AgentError(f"رفض Gemini الطلب (HTTP {response.status_code})")
            try:
                payload = response.json()
                parts = payload["candidates"][0]["content"]["parts"]
                text = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
                text = re.sub(r"\A```(?:json)?\s*|\s*```\Z", "", text, flags=re.I).strip()
                parsed = json.loads(text)
                if not isinstance(parsed, dict):
                    raise ValueError("JSON root must be an object")
                return parsed
            except (ValueError, KeyError, IndexError, TypeError):
                raise AgentError("أعاد النموذج استجابة JSON غير صالحة") from None
        raise AgentError(last_error)

    def plan(self, objective: str, project_map: dict[str, Any]) -> dict[str, Any]:
        model = choose_model(min(5, 1 + len(objective) // 500), "low", len(json.dumps(project_map)),
                             0.8, self.fast_model, self.reasoning_model)
        system = (
            "You are the planning role of a local software engineering agent. "
            "Return JSON only: summary, complexity (1-5), risk (low/medium/high/critical), "
            "tasks (array of {id,title,files,depends_on}), and checks (unit,compile,security,migrations,performance). "
            "List only files necessary for this task. Never request secrets, production data, deployments, "
            "database execution, commits, or network actions."
        )
        prompt = "OBJECTIVE:\n" + objective[:4000] + "\n\nPROJECT MAP (paths and metadata only):\n" + json.dumps(project_map, ensure_ascii=False)[:30000]
        plan = self._complete_json(system, prompt, model)
        plan["_model"] = model
        return plan

    def patch(self, objective: str, plan: dict[str, Any], context: dict[str, str], feedback: str = "") -> str:
        files = json.dumps(context, ensure_ascii=False)
        complexity = int(plan.get("complexity", 3) or 3)
        risk = str(plan.get("risk", "medium"))
        accuracy = 0.95 if risk in {"high", "critical"} else 0.82
        model = choose_model(complexity, risk, len(files), accuracy, self.fast_model, self.reasoning_model)
        system = (
            "You are the implementation role in a guarded local engineering agent. Return JSON only with keys "
            "summary and patch. patch must be a standard unified diff accepted by git apply. Modify only listed files. "
            "Do not delete or rename files, execute commands, edit secrets, alter production data, or introduce "
            "destructive database migrations. Keep changes minimal and add tests when practical."
        )
        prompt = (
            "OBJECTIVE:\n" + objective[:4000] + "\n\nPLAN:\n" + json.dumps(plan, ensure_ascii=False)[:16000]
            + "\n\nAVAILABLE FILE CONTENT (secret-like values redacted):\n" + files[:80000]
            + "\n\nPREVIOUS VALIDATION FEEDBACK:\n" + feedback[-8000:]
            + "\n\nReturn a minimal unified diff only in JSON field patch."
        )
        result = self._complete_json(system, prompt, model)
        patch = result.get("patch", "")
        if not isinstance(patch, str):
            raise AgentError("لم يُرجع النموذج نص patch")
        return patch
