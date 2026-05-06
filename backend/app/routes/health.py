from flask import Blueprint, current_app, jsonify, request


health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    config = current_app.config["APP_CONFIG"]
    live_check = request.args.get("check") == "live"
    reachable = None
    if live_check:
        reachable = current_app.extensions["gemini_classifier"].check_reachable()

    status_code = 200 if config.gemini_api_key or not live_check else 503
    return (
        jsonify(
            {
                "status": "ok" if status_code == 200 else "degraded",
                "gemini": {
                    "configured": bool(config.gemini_api_key),
                    "model": config.gemini_model,
                    "reachable": reachable,
                },
                "limits": {
                    "max_file_size_mb": config.max_file_size_mb,
                    "max_log_lines_per_request": config.max_log_lines_per_request,
                    "gemini_batch_size": config.gemini_batch_size,
                    "gemini_max_calls_per_request": config.gemini_max_calls_per_request,
                },
            }
        ),
        status_code,
    )
