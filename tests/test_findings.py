
import pytest

from toolkit.findings import (
    Finding,
    FindingCollection,
    Severity,
)


@pytest.fixture
def sample_finding():
    return Finding(
        title="Missing security header",
        description="A security response header is absent.",
        severity=Severity.MEDIUM,
        target="http://127.0.0.1:8080",
        recommendation="Review and configure appropriate security headers.",
        evidence="Synthetic test evidence.",
    )


def test_finding_creation(sample_finding):
    assert sample_finding.title == "Missing security header"
    assert sample_finding.severity == Severity.MEDIUM
    assert sample_finding.finding_id


def test_finding_to_dictionary(sample_finding):
    data = sample_finding.to_dict()

    assert data["severity"] == "Medium"
    assert data["target"] == "http://127.0.0.1:8080"


def test_empty_title_is_rejected():
    with pytest.raises(ValueError, match="title"):
        Finding(
            title=" ",
            description="Test",
            severity=Severity.LOW,
            target="http://127.0.0.1:8080",
            recommendation="Fix the issue.",
        )


def test_invalid_severity_is_rejected():
    with pytest.raises(ValueError, match="severity"):
        Finding(
            title="Test",
            description="Test description",
            severity="Unknown",
            target="http://127.0.0.1:8080",
            recommendation="Fix the issue.",
        )


def test_collection_add_and_count(sample_finding):
    collection = FindingCollection()
    collection.add(sample_finding)

    assert collection.count() == 1
    assert len(collection.all()) == 1


def test_duplicate_finding_is_rejected(sample_finding):
    collection = FindingCollection()
    collection.add(sample_finding)

    with pytest.raises(ValueError, match="Duplicate"):
        collection.add(sample_finding)


def test_severity_filter(sample_finding):
    collection = FindingCollection()
    collection.add(sample_finding)

    assert len(collection.by_severity(Severity.MEDIUM)) == 1
    assert len(collection.by_severity(Severity.HIGH)) == 0


def test_severity_summary(sample_finding):
    collection = FindingCollection()
    collection.add(sample_finding)

    summary = collection.summary()

    assert summary["Medium"] == 1
    assert summary["High"] == 0
    assert sum(summary.values()) == 1
