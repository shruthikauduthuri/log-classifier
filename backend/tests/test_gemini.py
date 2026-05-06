import json

import pytest

from app.config import AppConfig
from app.services.gemini import GeminiClassifier, GeminiServiceError


class FakeResponse:
    def __init__(self, text):
        self.text = text


@pytest.fixture
def config():
    return AppConfig(
        gemini_api_key="test",
        gemini_model="gemini-2.5-pro",
        max_file_size_mb=5,
        max_log_lines_per_request=100,
        max_log_line_chars=5000,
        gemini_batch_size=20,
        gemini_max_calls_per_request=5,
        gemini_retry_attempts=1,
        high_threshold=0.7,
        medium_threshold=0.4,
        allowed_origins=["http://localhost:5173"],
        rate_limit_default="100 per minute",
        rate_limit_classify="30 per minute",
        rate_limit_storage_uri="memory://",
        testing=True,
    )


def test_parse_response_orders_by_index(config):
    classifier = GeminiClassifier(config)
    response = FakeResponse(
        json.dumps(
            {
                "items": [
                    {
                        "index": 1,
                        "score": 0.2,
                        "tier": "LOW",
                        "reason": "Routine job",
                        "source": "Syslog",
                        "event_type": "General Log",
                    },
                    {
                        "index": 0,
                        "score": 0.9,
                        "tier": "HIGH",
                        "reason": "Failed root login",
                        "source": "Auth",
                        "event_type": "Authentication",
                    },
                ]
            }
        )
    )
    results = classifier._parse_response(response, ["login failed", "cron done"], "Unknown")
    assert results[0]["score"] == 0.9
    assert results[1]["source"] == "Syslog"


def test_parse_response_rejects_invalid_json(config):
    classifier = GeminiClassifier(config)
    with pytest.raises(GeminiServiceError):
        classifier._parse_response(FakeResponse("not json"), ["line"], "Unknown")


def test_parse_response_rejects_wrong_count(config):
    classifier = GeminiClassifier(config)
    with pytest.raises(GeminiServiceError):
        classifier._parse_response(FakeResponse(json.dumps({"items": []})), ["line"], "Unknown")


def test_missing_key_is_sanitized(config):
    config.gemini_api_key = ""
    classifier = GeminiClassifier(config)
    with pytest.raises(GeminiServiceError):
        classifier.classify_batch(["line"])
