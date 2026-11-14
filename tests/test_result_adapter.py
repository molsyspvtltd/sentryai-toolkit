
import json

import pytest

from toolkit.config import SentryAIConfig
from toolkit.findings import Severity
from toolkit.result_adapter import findings_from_json


CONFIG = SentryAIConfig(
    target_url="http://127.0.0.1:4280",
    testing_scope="local-dvwa",
)

TARGET = CONFIG.target_url


def sample_payload():
    return json.dumps({
        "findings": [
            {
                "title": "Sample finding",
                "description": "This is test data, not a real vulnerability.",
                "severity": "Medium",
                "target": TARGET,
                "recommendation": "Review the relevant application configuration.",
                "evidence": "Synthetic test evidence",
                "source": "SampleData",
            }
        ]
    })


def test_valid_json_converts_to_finding_collection():
    result = findings_from_json(sample_payload(), CONFIG)

    assert result.count() == 1
    finding = result.all()[0]
    assert finding.title == "Sample finding"
    assert finding.severity == Severity.MEDIUM
    assert finding.source == "SampleData"


def test_empty_findings_returns_empty_collection():
    result = findings_from_json('{"findings": []}', CONFIG)

    assert result.count() == 0


def test_invalid_json_is_rejected():
    with pytest.raises(ValueError, match="Invalid JSON"):
        findings_from_json("{invalid json}", CONFIG)


def test_missing_required_field_is_rejected():
    payload = json.dumps({
        "findings": [
            {
                "title": "Incomplete finding",
                "severity": "Low",
                "target": TARGET,
            }
        ]
    })

    with pytest.raises(ValueError, match="missing fields"):
        findings_from_json(payload, CONFIG)


def test_invalid_severity_is_rejected():
    payload = json.dumps({
        "findings": [
            {
                "title": "Sample",
                "description": "Description",
                "severity": "Unknown",
                "target": TARGET,
                "recommendation": "Review configuration.",
            }
        ]
    })

    with pytest.raises(ValueError, match="invalid severity"):
        findings_from_json(payload, CONFIG)


def test_unexpected_target_is_rejected():
    payload = json.dumps({
        "findings": [
            {
                "title": "Sample",
                "description": "Description",
                "severity": "Low",
                "target": "https://example.com",
                "recommendation": "Review configuration.",
            }
        ]
    })

    with pytest.raises(ValueError, match="unexpected target"):
        findings_from_json(payload, CONFIG)


def test_non_string_payload_is_rejected():
    with pytest.raises(TypeError):
        findings_from_json({}, CONFIG)


def test_neurosploit_native_array_is_supported():
    payload = json.dumps([
        {
            "id": "ns-001",
            "agent": "test-agent",
            "title": "Sample NeuroSploit finding",
            "severity": "high",
            "endpoint": TARGET,
            "impact": "Synthetic impact description.",
            "evidence": "Synthetic evidence.",
            "remediation": "Review the application configuration.",
            "cwe": "CWE-79",
            "cvss": "7.1",
            "confidence": 0.9,
            "validated": True,
        }
    ])

    result = findings_from_json(payload, CONFIG)

    assert result.count() == 1

    finding = result.all()[0]
    assert finding.title == "Sample NeuroSploit finding"
    assert finding.severity == Severity.HIGH
    assert finding.source == "NeuroSploit"
    assert finding.finding_id == "ns-001"
    assert finding.target == TARGET
    assert "CWE-79" in finding.evidence


def test_neurosploit_info_severity_is_supported():
    payload = json.dumps([
        {
            "id": "ns-002",
            "title": "Informational sample",
            "severity": "Info",
            "endpoint": TARGET,
        }
    ])

    result = findings_from_json(payload, CONFIG)

    assert result.all()[0].severity == Severity.INFORMATIONAL


def test_neurosploit_empty_array_returns_empty_collection():
    result = findings_from_json("[]", CONFIG)

    assert result.count() == 0


def test_neurosploit_external_endpoint_is_rejected():
    payload = json.dumps([
        {
            "id": "ns-003",
            "title": "Unexpected target",
            "severity": "High",
            "endpoint": "https://example.com",
        }
    ])

    with pytest.raises(ValueError, match="unexpected target"):
        findings_from_json(payload, CONFIG)


def test_neurosploit_missing_title_is_rejected():
    payload = json.dumps([
        {
            "id": "ns-004",
            "severity": "Medium",
            "endpoint": TARGET,
        }
    ])

    with pytest.raises(ValueError, match="invalid title"):
        findings_from_json(payload, CONFIG)
