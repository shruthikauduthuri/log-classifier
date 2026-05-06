import os
from dataclasses import dataclass


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
ALLOWED_GEMINI_MODELS = {
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
}


def _env_int(name, default):
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return int(raw)


def _env_float(name, default):
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return float(raw)


def _env_csv(name, default):
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass
class AppConfig:
    gemini_api_key: str
    gemini_model: str
    max_file_size_mb: int
    max_log_lines_per_request: int
    max_log_line_chars: int
    gemini_batch_size: int
    gemini_max_calls_per_request: int
    gemini_retry_attempts: int
    high_threshold: float
    medium_threshold: float
    allowed_origins: list[str]
    rate_limit_default: str
    rate_limit_classify: str
    rate_limit_storage_uri: str
    testing: bool = False

    @property
    def max_file_size_bytes(self):
        return self.max_file_size_mb * 1024 * 1024

    @classmethod
    def from_env(cls):
        model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
        if model not in ALLOWED_GEMINI_MODELS:
            allowed = ", ".join(sorted(ALLOWED_GEMINI_MODELS))
            raise ValueError(f"Unsupported Gemini model. Use one of: {allowed}.")

        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
            gemini_model=model,
            max_file_size_mb=_env_int("MAX_FILE_SIZE_MB", 5),
            max_log_lines_per_request=_env_int("MAX_LOG_LINES_PER_REQUEST", 100),
            max_log_line_chars=_env_int("MAX_LOG_LINE_CHARS", 5000),
            gemini_batch_size=min(_env_int("GEMINI_BATCH_SIZE", 20), 20),
            gemini_max_calls_per_request=_env_int("GEMINI_MAX_CALLS_PER_REQUEST", 5),
            gemini_retry_attempts=_env_int("GEMINI_RETRY_ATTEMPTS", 3),
            high_threshold=_env_float("HIGH_THRESHOLD", 0.70),
            medium_threshold=_env_float("MEDIUM_THRESHOLD", 0.40),
            allowed_origins=_env_csv(
                "ALLOWED_ORIGINS",
                [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://localhost:5174",
                    "http://127.0.0.1:5174",
                ],
            ),
            rate_limit_default=os.getenv("RATE_LIMIT_DEFAULT", "100 per minute"),
            rate_limit_classify=os.getenv("RATE_LIMIT_CLASSIFY", "30 per minute"),
            rate_limit_storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
            testing=os.getenv("TESTING", "").lower() == "true",
        )
