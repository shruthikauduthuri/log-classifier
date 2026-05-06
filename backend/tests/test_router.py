from app.services.router import (
    destination_for_tier,
    enrich_result,
    infer_event_type,
    infer_source,
    summarize_results,
    tier_for_score,
)


def test_tier_for_score_respects_thresholds():
    assert tier_for_score(0.7) == "HIGH"
    assert tier_for_score(0.4) == "MEDIUM"
    assert tier_for_score(0.39) == "LOW"
    assert tier_for_score(1.5) == "HIGH"


def test_destination_mapping():
    assert destination_for_tier("HIGH") == "SIEM"
    assert destination_for_tier("MEDIUM") == "DataLake"
    assert destination_for_tier("LOW") == "ColdStorage"


def test_infer_source_and_event_type():
    raw = "May 05 host sshd[20]: Failed password for root"
    assert infer_source(raw) == "Auth"
    assert infer_event_type(raw) == "Authentication"


def test_enrich_result_recomputes_tier_from_score():
    result = enrich_result(
        "firewall deny src=10.0.0.4",
        {"score": 0.8, "tier": "LOW", "reason": "Suspicious deny"},
        "Unknown",
        0.7,
        0.4,
    )
    assert result["tier"] == "HIGH"
    assert result["destination"] == "SIEM"
    assert result["source"] == "Firewall"


def test_summarize_results():
    results = [
        {"tier": "HIGH", "score": 0.9},
        {"tier": "MEDIUM", "score": 0.5},
        {"tier": "LOW", "score": 0.1},
    ]
    summary = summarize_results(results)
    assert summary["total"] == 3
    assert summary["siem_savings_pct"] == 66.7
    assert summary["estimated_monthly_savings"] == 8004.0
