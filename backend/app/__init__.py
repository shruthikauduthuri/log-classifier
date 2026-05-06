from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from app.config import AppConfig
from app.services.gemini import GeminiClassifier
from app.utils.errors import register_error_handlers


limiter = Limiter(key_func=get_remote_address)


def create_app(config_overrides=None):
    load_dotenv()

    app = Flask(__name__)
    config = AppConfig.from_env()
    if config_overrides:
        for key, value in config_overrides.items():
            setattr(config, key, value)

    app.config["APP_CONFIG"] = config
    app.config["MAX_CONTENT_LENGTH"] = config.max_file_size_bytes
    app.config["RATELIMIT_ENABLED"] = not config.testing
    app.config["RATELIMIT_STORAGE_URI"] = config.rate_limit_storage_uri
    app.config["RATELIMIT_DEFAULT"] = config.rate_limit_default

    CORS(
        app,
        resources={r"/api/*": {"origins": config.allowed_origins}},
        supports_credentials=False,
    )

    limiter.init_app(app)

    app.extensions["gemini_classifier"] = GeminiClassifier(config)

    from app.routes.classify import classify_bp
    from app.routes.health import health_bp

    register_error_handlers(app)
    app.register_blueprint(health_bp)
    app.register_blueprint(classify_bp)

    @app.after_request
    def apply_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cache-Control"] = "no-store"
        return response

    return app
