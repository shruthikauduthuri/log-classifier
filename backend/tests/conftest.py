import json

import pytest

from app import create_app


class FakeGeminiClassifier:
    def __init__(self, scores=None):
        self.scores = scores or [0.9, 0.55, 0.15]
        self.calls = []

    def check_reachable(self):
        return True

    def classify_batch(self, logs, source_hint="Unknown"):
        self.calls.append({"logs": logs, "source_hint": source_hint})
        items = []
        for index, log in enumerate(logs):
            score = self.scores[index % len(self.scores)]
            items.append(
                {
                    "score": score,
                    "tier": "HIGH" if score >= 0.7 else "MEDIUM" if score >= 0.4 else "LOW",
                    "reason": f"Mock rationale for {index}",
                    "source": source_hint if source_hint != "Unknown" else "Auth",
                    "event_type": "Authentication" if "login" in log.lower() else "General Log",
                }
            )
        return items


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-pro")
    monkeypatch.setenv("MAX_LOG_LINES_PER_REQUEST", "100")
    monkeypatch.setenv("GEMINI_BATCH_SIZE", "20")
    monkeypatch.setenv("GEMINI_MAX_CALLS_PER_REQUEST", "5")
    flask_app = create_app()
    flask_app.extensions["gemini_classifier"] = FakeGeminiClassifier()
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def parse_ndjson(response):
    return [json.loads(line) for line in response.get_data(as_text=True).splitlines() if line]
