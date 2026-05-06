import json
import time

from app.services.router import infer_event_type, infer_source


class GeminiServiceError(Exception):
    pass


class GeminiQuotaError(GeminiServiceError):
    pass


class GeminiClassifier:
    def __init__(self, config):
        self.config = config
        self.client = None

    def _client(self):
        if not self.config.gemini_api_key:
            raise GeminiServiceError("Gemini API key is not configured.")
        if self.client is None:
            try:
                from google import genai
            except ImportError as exc:
                raise GeminiServiceError("Gemini SDK is not installed.") from exc
            self.client = genai.Client(api_key=self.config.gemini_api_key)
        return self.client

    def check_reachable(self):
        if not self.config.gemini_api_key:
            return False
        try:
            self._client().models.generate_content(
                model=self.config.gemini_model,
                contents="Return only the word ok.",
            )
            return True
        except Exception:
            return False

    def classify_batch(self, logs, source_hint="Unknown"):
        if not logs:
            return []

        prompt = self._build_prompt(logs, source_hint)
        schema = self._response_schema(len(logs))
        last_error = None

        for attempt in range(self.config.gemini_retry_attempts):
            try:
                response = self._client().models.generate_content(
                    model=self.config.gemini_model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": schema,
                    },
                )
                return self._parse_response(response, logs, source_hint)
            except Exception as exc:
                last_error = exc
                if self._is_quota_error(exc):
                    raise GeminiQuotaError("Gemini quota exhausted for configured model.") from exc
                if attempt < self.config.gemini_retry_attempts - 1:
                    time.sleep(min(2**attempt, 8))

        raise GeminiServiceError("Gemini classification failed.") from last_error

    def _is_quota_error(self, error):
        status_code = getattr(error, "status_code", None)
        if status_code == 429:
            return True
        message = str(error).lower()
        return "resource_exhausted" in message or "quota" in message

    def _build_prompt(self, logs, source_hint):
        lines = "\n".join(f"{index}. {log}" for index, log in enumerate(logs))
        return f"""
You are a security log relevance classifier for a SIEM routing dashboard.
Score each log entry for security investigation value from 0.0 to 1.0.
Use HIGH for scores >= 0.70, MEDIUM for scores >= 0.40 and < 0.70, LOW otherwise.
Return JSON only. Do not include markdown or commentary.
The optional source hint is: {source_hint}.
Reason must be 120 characters or fewer and must not include secrets.

Logs:
{lines}
""".strip()

    def _response_schema(self, expected_count):
        return {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "minItems": expected_count,
                    "maxItems": expected_count,
                    "items": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "integer"},
                            "score": {"type": "number"},
                            "tier": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                            "reason": {"type": "string"},
                            "source": {
                                "type": "string",
                                "enum": ["Firewall", "Auth", "Syslog", "DNS", "App", "Network", "Unknown"],
                            },
                            "event_type": {"type": "string"},
                        },
                        "required": ["index", "score", "tier", "reason", "source", "event_type"],
                    },
                }
            },
            "required": ["items"],
        }

    def _parse_response(self, response, logs, source_hint):
        raw_text = getattr(response, "text", "") or ""
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise GeminiServiceError("Gemini returned invalid JSON.") from exc

        items = payload.get("items")
        if not isinstance(items, list) or len(items) != len(logs):
            raise GeminiServiceError("Gemini returned an unexpected result count.")

        by_index = {}
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("index"), int):
                by_index[item["index"]] = item

        normalized = []
        for index, log in enumerate(logs):
            item = by_index.get(index, {})
            normalized.append(
                {
                    "score": item.get("score", 0),
                    "tier": item.get("tier", "LOW"),
                    "reason": item.get("reason", "Classified from security relevance signals."),
                    "source": item.get("source") or infer_source(log, source_hint),
                    "event_type": item.get("event_type") or infer_event_type(log),
                }
            )
        return normalized
