from dataclasses import dataclass
from typing import Any

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.utils.errors import ApiError


SUPPORTED_EXTENSIONS = {".log", ".txt"}
SUPPORTED_SOURCES = {"Firewall", "Auth", "Syslog", "DNS", "App", "Network", "Unknown"}


@dataclass
class ClassificationRequest:
    logs: list[str]
    source_hint: str
    high_threshold: float
    medium_threshold: float


def chunked(items, size):
    for index in range(0, len(items), size):
        yield items[index : index + size]


def normalize_lines(lines: list[Any], config) -> list[str]:
    if not isinstance(lines, list):
        raise ApiError("logs must be an array of strings.")

    normalized = []
    for item in lines:
        if not isinstance(item, str):
            raise ApiError("Each log entry must be a string.")
        value = item.strip()
        if not value:
            continue
        if len(value) > config.max_log_line_chars:
            raise ApiError(
                f"Each log entry must be {config.max_log_line_chars} characters or fewer.",
                413,
                "log_line_too_large",
            )
        normalized.append(value)

    if not normalized:
        raise ApiError("At least one non-empty log line is required.")
    if len(normalized) > config.max_log_lines_per_request:
        raise ApiError(
            f"Maximum {config.max_log_lines_per_request} log lines per request for the configured tier.",
            413,
            "too_many_log_lines",
        )

    return normalized


def validate_thresholds(high_threshold, medium_threshold):
    try:
        high = float(high_threshold)
        medium = float(medium_threshold)
    except (TypeError, ValueError) as exc:
        raise ApiError("Thresholds must be numbers between 0 and 1.") from exc

    if not 0 <= medium < high <= 1:
        raise ApiError("Thresholds must satisfy 0 <= medium < high <= 1.")
    return high, medium


def validate_source_hint(value):
    if value in (None, ""):
        return "Unknown"
    if not isinstance(value, str):
        raise ApiError("source_hint must be a string.")
    normalized = value.strip().title()
    source_aliases = {
        "Firewall": "Firewall",
        "Auth": "Auth",
        "Authentication": "Auth",
        "Syslog": "Syslog",
        "Dns": "DNS",
        "DNS": "DNS",
        "App": "App",
        "Application": "App",
        "Network": "Network",
        "Unknown": "Unknown",
    }
    source = source_aliases.get(normalized, "Unknown")
    if source not in SUPPORTED_SOURCES:
        return "Unknown"
    return source


def parse_json_payload(data, config):
    if not isinstance(data, dict):
        raise ApiError("Request body must be a JSON object.")

    high, medium = validate_thresholds(
        data.get("high_threshold", config.high_threshold),
        data.get("medium_threshold", config.medium_threshold),
    )
    return ClassificationRequest(
        logs=normalize_lines(data.get("logs", []), config),
        source_hint=validate_source_hint(data.get("source_hint")),
        high_threshold=high,
        medium_threshold=medium,
    )


def _validate_filename(file: FileStorage):
    filename = secure_filename(file.filename or "")
    if not filename:
        raise ApiError("A .txt or .log file is required.", 400, "missing_file")
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ApiError("Only .txt and .log files are supported.", 415, "unsupported_media_type")


def parse_file_payload(file: FileStorage, form, config):
    _validate_filename(file)
    content_type = (file.mimetype or "").lower()
    if content_type and not (
        content_type.startswith("text/")
        or content_type in {"application/octet-stream", "application/x-log"}
    ):
        raise ApiError("Only plain-text uploads are supported.", 415, "unsupported_media_type")

    raw = file.stream.read(config.max_file_size_bytes + 1)
    if len(raw) > config.max_file_size_bytes:
        raise ApiError(
            f"File must be {config.max_file_size_mb} MB or smaller.",
            413,
            "file_too_large",
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ApiError("Uploaded logs must be UTF-8 encoded.", 415, "invalid_encoding") from exc

    high, medium = validate_thresholds(
        form.get("high_threshold", config.high_threshold),
        form.get("medium_threshold", config.medium_threshold),
    )
    return ClassificationRequest(
        logs=normalize_lines(text.splitlines(), config),
        source_hint=validate_source_hint(form.get("source_hint")),
        high_threshold=high,
        medium_threshold=medium,
    )


def validate_quota(requested_log_count, config):
    calls_required = (requested_log_count + config.gemini_batch_size - 1) // config.gemini_batch_size
    if calls_required > config.gemini_max_calls_per_request:
        raise ApiError(
            (
                "Request would exceed the configured Gemini free-tier guardrail. "
                f"Reduce lines or raise GEMINI_MAX_CALLS_PER_REQUEST intentionally."
            ),
            429,
            "quota_guardrail",
        )
    return {
        "batch_size": config.gemini_batch_size,
        "max_calls_per_request": config.gemini_max_calls_per_request,
        "calls_required": calls_required,
        "max_lines_per_request": config.max_log_lines_per_request,
    }
