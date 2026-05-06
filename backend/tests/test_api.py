from io import BytesIO

import json


def parse_ndjson(response):
    return [json.loads(line) for line in response.get_data(as_text=True).splitlines() if line]


def test_health_does_not_do_live_check_by_default(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["gemini"]["configured"] is True
    assert body["gemini"]["model"] == "gemini-2.5-pro"
    assert body["gemini"]["reachable"] is None
    assert "X-Content-Type-Options" in response.headers


def test_classify_json(client):
    response = client.post(
        "/api/classify",
        json={
            "logs": [
                "sshd failed login for root",
                "nginx 404 health check",
                "cron completed",
            ],
            "source_hint": "Auth",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["summary"]["total"] == 3
    assert body["summary"]["high_count"] == 1
    assert body["summary"]["medium_count"] == 1
    assert body["summary"]["low_count"] == 1
    assert body["results"][0]["destination"] == "SIEM"
    assert "test-key" not in response.get_data(as_text=True)


def test_classify_multipart(client):
    response = client.post(
        "/api/classify",
        data={
            "file": (BytesIO(b"sshd failed login\nkernel info"), "events.log"),
            "source_hint": "Syslog",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json()["summary"]["total"] == 2


def test_classify_rejects_html_upload(client):
    response = client.post(
        "/api/classify",
        data={"file": (BytesIO(b"<script>bad</script>"), "events.html")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 415


def test_stream_classify(client):
    response = client.post(
        "/api/classify/stream",
        json={"logs": ["sshd failed login", "nginx 404"], "source_hint": "Auth"},
    )
    assert response.status_code == 200
    events = parse_ndjson(response)
    assert events[0]["type"] == "accepted"
    assert events[1]["type"] == "batch_complete"
    assert events[-1]["type"] == "complete"
    assert events[-1]["summary"]["total"] == 2


def test_classify_rejects_unsupported_content_type(client):
    response = client.post("/api/classify", data="raw")
    assert response.status_code == 415


def test_classify_quota_guardrail(client, monkeypatch):
    monkeypatch.setenv("MAX_LOG_LINES_PER_REQUEST", "120")
    monkeypatch.setenv("GEMINI_BATCH_SIZE", "20")
    monkeypatch.setenv("GEMINI_MAX_CALLS_PER_REQUEST", "1")

    from app import create_app

    flask_app = create_app()
    flask_app.extensions["gemini_classifier"] = client.application.extensions["gemini_classifier"]
    local_client = flask_app.test_client()
    response = local_client.post("/api/classify", json={"logs": [f"line {i}" for i in range(21)]})
    assert response.status_code == 429
