
import json

from toolkit.findings import Finding, FindingCollection, Severity
from toolkit.reporting import (
    generate_json_report,
    generate_markdown_report,
)


def create_collection():
    collection = FindingCollection()

    collection.add(
        Finding(
            title="Synthetic security finding",
            description="This is a sample finding for report testing.",
            severity=Severity.HIGH,
            target="http://127.0.0.1:8080",
            recommendation="Review the affected application configuration.",
            evidence="Synthetic evidence for automated testing.",
        )
    )

    return collection


def test_json_report_generation(tmp_path):
    collection = create_collection()

    report_path = generate_json_report(collection, tmp_path)

    assert report_path.exists()

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    assert report["project"] == "SentryAI"
    assert report["total_findings"] == 1
    assert report["severity_summary"]["High"] == 1
    assert len(report["findings"]) == 1


def test_markdown_report_generation(tmp_path):
    collection = create_collection()

    report_path = generate_markdown_report(
        collection,
        tmp_path,
    )

    assert report_path.exists()

    content = report_path.read_text(encoding="utf-8")

    assert "SentryAI Security Assessment Report" in content
    assert "Synthetic security finding" in content
    assert "High" in content
    assert "Recommendation" in content


def test_empty_collection_report(tmp_path):
    collection = FindingCollection()

    report_path = generate_markdown_report(
        collection,
        tmp_path,
    )

    content = report_path.read_text(encoding="utf-8")

    assert "No findings were recorded." in content
