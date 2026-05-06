import re
from statistics import mean


DESTINATIONS = {
    "HIGH": "SIEM",
    "MEDIUM": "DataLake",
    "LOW": "ColdStorage",
}

SOURCE_PATTERNS = [
    ("Firewall", re.compile(r"\b(firewall|fortigate|palo alto|deny|allowed|acl)\b", re.I)),
    ("Auth", re.compile(r"\b(auth|sshd|login|password|mfa|kerberos|ldap|okta)\b", re.I)),
    ("DNS", re.compile(r"\b(dns|query|resolver|named|bind)\b", re.I)),
    ("Network", re.compile(r"\b(tcp|udp|icmp|netflow|switch|router|vpn)\b", re.I)),
    ("App", re.compile(r"\b(http|api|exception|traceback|nginx|apache|status=|404|500)\b", re.I)),
    ("Syslog", re.compile(r"\b(syslog|kernel|cron|systemd|daemon)\b", re.I)),
]

EVENT_PATTERNS = [
    ("Authentication", re.compile(r"\b(login|password|mfa|auth|sshd|kerberos)\b", re.I)),
    ("Network Access", re.compile(r"\b(tcp|udp|icmp|port|connection|deny|allow)\b", re.I)),
    ("DNS Query", re.compile(r"\b(dns|query|resolver)\b", re.I)),
    ("Application Error", re.compile(r"\b(exception|traceback|error|500|stack)\b", re.I)),
    ("Web Request", re.compile(r"\b(http|nginx|apache|404|user-agent)\b", re.I)),
]


def tier_for_score(score, high_threshold=0.70, medium_threshold=0.40):
    score = clamp_score(score)
    if score >= high_threshold:
        return "HIGH"
    if score >= medium_threshold:
        return "MEDIUM"
    return "LOW"


def destination_for_tier(tier):
    return DESTINATIONS.get(tier, "ColdStorage")


def clamp_score(value):
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, score))


def infer_source(raw, source_hint="Unknown"):
    if source_hint and source_hint != "Unknown":
        return source_hint
    for source, pattern in SOURCE_PATTERNS:
        if pattern.search(raw):
            return source
    return "Syslog"


def infer_event_type(raw):
    for event_type, pattern in EVENT_PATTERNS:
        if pattern.search(raw):
            return event_type
    return "General Log"


def enrich_result(raw, ai_result, source_hint, high_threshold, medium_threshold):
    score = clamp_score(ai_result.get("score"))
    tier = tier_for_score(score, high_threshold, medium_threshold)
    source = ai_result.get("source") or infer_source(raw, source_hint)
    event_type = ai_result.get("event_type") or infer_event_type(raw)
    reason = str(ai_result.get("reason") or "Classified from security relevance signals.").strip()
    if len(reason) > 120:
        reason = reason[:117].rstrip() + "..."

    return {
        "raw": raw,
        "score": round(score, 3),
        "tier": tier,
        "destination": destination_for_tier(tier),
        "reason": reason,
        "source": source,
        "event_type": event_type,
    }


def summarize_results(results):
    total = len(results)
    high = [item for item in results if item["tier"] == "HIGH"]
    medium = [item for item in results if item["tier"] == "MEDIUM"]
    low = [item for item in results if item["tier"] == "LOW"]
    filtered_count = len(medium) + len(low)
    savings_pct = round((filtered_count / total) * 100, 1) if total else 0.0
    estimated_monthly_savings = round(savings_pct / 100 * 12000, 2)

    def avg(items):
        return round(mean([item["score"] for item in items]), 3) if items else 0.0

    return {
        "total": total,
        "high_count": len(high),
        "medium_count": len(medium),
        "low_count": len(low),
        "siem_savings_pct": savings_pct,
        "filtered_count": filtered_count,
        "estimated_monthly_savings": estimated_monthly_savings,
        "average_scores": {
            "HIGH": avg(high),
            "MEDIUM": avg(medium),
            "LOW": avg(low),
        },
    }
