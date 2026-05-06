from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage, MultiDict

from app.config import AppConfig
from app.utils.errors import ApiError
from app.utils.validators import (
    normalize_lines,
    parse_file_payload,
    parse_json_payload,
    validate_quota,
    validate_source_hint,
    validate_thresholds,
)


@pytest.fixture
def config():
    return AppConfig(
        gemini_api_key="test",
        gemini_model="gemini-2.5-pro",
        max_file_size_mb=1,
        max_log_lines_per_request=3,
        max_log_line_chars=20,
        gemini_batch_size=2,
        gemini_max_calls_per_request=2,
        gemini_retry_attempts=1,
        high_threshold=0.7,
        medium_threshold=0.4,
        allowed_origins=["http://localhost:5173"],
        rate_limit_default="100 per minute",
        rate_limit_classify="30 per minute",
        rate_limit_storage_uri="memory://",
        testing=True,
    )


def test_normalize_lines_trims_and_rejects_empty(config):
    assert normalize_lines([" one ", "", "two"], config) == ["one", "two"]


def test_normalize_lines_limits_count(config):
    with pytest.raises(ApiError) as error:
        normalize_lines(["a", "b", "c", "d"], config)
    assert error.value.code == "too_many_log_lines"


def test_normalize_lines_limits_line_length(config):
    with pytest.raises(ApiError) as error:
        normalize_lines(["x" * 21], config)
    assert error.value.code == "log_line_too_large"


def test_validate_thresholds():
    assert validate_thresholds("0.8", "0.3") == (0.8, 0.3)
    with pytest.raises(ApiError):
        validate_thresholds(0.3, 0.4)


def test_validate_source_hint_aliases():
    assert validate_source_hint("dns") == "DNS"
    assert validate_source_hint("authentication") == "Auth"
    assert validate_source_hint("unknown-value") == "Unknown"


def test_parse_json_payload(config):
    parsed = parse_json_payload({"logs": ["a", "b"], "source_hint": "auth"}, config)
    assert parsed.logs == ["a", "b"]
    assert parsed.source_hint == "Auth"


def test_parse_file_payload(config):
    file = FileStorage(stream=BytesIO(b"line one\nline two"), filename="sample.log", content_type="text/plain")
    parsed = parse_file_payload(file, MultiDict({"source_hint": "Firewall"}), config)
    assert parsed.logs == ["line one", "line two"]
    assert parsed.source_hint == "Firewall"


def test_parse_file_payload_rejects_extension(config):
    file = FileStorage(stream=BytesIO(b"line"), filename="sample.exe", content_type="text/plain")
    with pytest.raises(ApiError) as error:
        parse_file_payload(file, MultiDict(), config)
    assert error.value.status_code == 415


def test_validate_quota(config):
    assert validate_quota(3, config)["calls_required"] == 2
    with pytest.raises(ApiError) as error:
        validate_quota(5, config)
    assert error.value.code == "quota_guardrail"
