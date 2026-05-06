import json
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from app import limiter
from app.services.gemini import GeminiQuotaError, GeminiServiceError
from app.services.router import enrich_result, summarize_results
from app.utils.errors import ApiError
from app.utils.validators import (
    chunked,
    parse_file_payload,
    parse_json_payload,
    validate_quota,
)


classify_bp = Blueprint("classify", __name__, url_prefix="/api")


def _parse_request(config):
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        file = request.files.get("file")
        if file is None:
            raise ApiError("Multipart requests must include a file field.", 400, "missing_file")
        return parse_file_payload(file, request.form, config)

    if not request.is_json:
        raise ApiError("Use application/json or multipart/form-data.", 415, "unsupported_media_type")
    return parse_json_payload(request.get_json(silent=True), config)


def _classify_batch(classifier, logs, source_hint, high_threshold, medium_threshold):
    ai_results = classifier.classify_batch(logs, source_hint)
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            **enrich_result(raw, ai_result, source_hint, high_threshold, medium_threshold),
            "timestamp": now,
        }
        for raw, ai_result in zip(logs, ai_results)
    ]


@classify_bp.post("/classify")
@limiter.limit(lambda: current_app.config["APP_CONFIG"].rate_limit_classify)
def classify():
    config = current_app.config["APP_CONFIG"]
    payload = _parse_request(config)
    quota = validate_quota(len(payload.logs), config)
    classifier = current_app.extensions["gemini_classifier"]

    try:
        results = []
        for batch in chunked(payload.logs, config.gemini_batch_size):
            results.extend(
                _classify_batch(
                    classifier,
                    batch,
                    payload.source_hint,
                    payload.high_threshold,
                    payload.medium_threshold,
                )
            )
    except GeminiQuotaError as exc:
        raise ApiError(
            "Gemini quota is exhausted for the configured model. Use gemini-2.5-flash for free-tier testing or enable quota for gemini-2.5-pro.",
            429,
            "gemini_quota_exhausted",
        ) from exc
    except GeminiServiceError as exc:
        raise ApiError("Gemini classification is unavailable. Try again later.", 503, "gemini_unavailable") from exc

    return jsonify({"results": results, "summary": summarize_results(results), "quota": quota})


@classify_bp.post("/classify/stream")
@limiter.limit(lambda: current_app.config["APP_CONFIG"].rate_limit_classify)
def classify_stream():
    config = current_app.config["APP_CONFIG"]
    payload = _parse_request(config)
    quota = validate_quota(len(payload.logs), config)
    classifier = current_app.extensions["gemini_classifier"]

    def emit(event):
        return json.dumps(event, separators=(",", ":")) + "\n"

    @stream_with_context
    def generate():
        results = []
        batches = list(chunked(payload.logs, config.gemini_batch_size))
        yield emit({"type": "accepted", "total": len(payload.logs), "batches": len(batches), "quota": quota})

        for index, batch in enumerate(batches, start=1):
            try:
                batch_results = _classify_batch(
                    classifier,
                    batch,
                    payload.source_hint,
                    payload.high_threshold,
                    payload.medium_threshold,
                )
            except GeminiQuotaError:
                yield emit(
                    {
                        "type": "error",
                        "code": "gemini_quota_exhausted",
                        "message": "Gemini quota is exhausted for the configured model. Use gemini-2.5-flash for free-tier testing or enable quota for gemini-2.5-pro.",
                    }
                )
                return
            except GeminiServiceError:
                yield emit(
                    {
                        "type": "error",
                        "code": "gemini_unavailable",
                        "message": "Gemini classification is unavailable. Try again later.",
                    }
                )
                return

            results.extend(batch_results)
            yield emit(
                {
                    "type": "batch_complete",
                    "batch": index,
                    "batches": len(batches),
                    "results": batch_results,
                    "summary": summarize_results(results),
                }
            )

        yield emit({"type": "complete", "results": results, "summary": summarize_results(results), "quota": quota})

    return Response(generate(), mimetype="application/x-ndjson")
