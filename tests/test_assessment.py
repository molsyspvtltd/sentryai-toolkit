"""Tests for the SentryAI assessment workflow."""

from toolkit.assessment import (
    AssessmentStatus,
    AssessmentWorkflow,
)
from toolkit.config import SentryAIConfig
from toolkit.findings import (
    Finding,
    FindingCollection,
    Severity,
)


def create_config(output_dir):
    return SentryAIConfig(
        target_url="http://localhost:8080",
        testing_scope="local-dvwa",
        output_dir=output_dir,
    )


def create_findings():
    findings = FindingCollection()

    findings.add(
        Finding(
            title="Test security finding",
            description="A sample finding for workflow testing.",
            severity=Severity.MEDIUM,
            target="http://localhost:8080",
            recommendation="Review the affected application component.",
            evidence="Synthetic test evidence.",
            source="MockScanner",
        )
    )

    return findings


def test_successful_assessment_generates_reports(tmp_path):
    config = create_config(tmp_path)
    expected_findings = create_findings()

    def mock_scanner(received_config):
        assert received_config is config
        return expected_findings

    workflow = AssessmentWorkflow(config, mock_scanner)
    result = workflow.run()

    assert result.status == AssessmentStatus.COMPLETED
    assert workflow.status == AssessmentStatus.COMPLETED
    assert result.findings.count() == 1
    assert result.json_report.exists()
    assert result.markdown_report.exists()


def test_empty_findings_complete_successfully(tmp_path):
    config = create_config(tmp_path)

    workflow = AssessmentWorkflow(
        config,
        lambda received_config: FindingCollection(),
    )

    result = workflow.run()

    assert result.status == AssessmentStatus.COMPLETED
    assert result.findings.count() == 0
    assert result.json_report.exists()
    assert result.markdown_report.exists()


def test_invalid_target_prevents_scanner_execution(tmp_path):
    config = SentryAIConfig(
        target_url="https://example.com",
        testing_scope="local-dvwa",
        output_dir=tmp_path,
    )

    scanner_called = False

    def mock_scanner(received_config):
        nonlocal scanner_called
        scanner_called = True
        return FindingCollection()

    workflow = AssessmentWorkflow(config, mock_scanner)
    result = workflow.run()

    assert result.status == AssessmentStatus.FAILED
    assert scanner_called is False
    assert result.error is not None


def test_scanner_failure_is_recorded(tmp_path):
    config = create_config(tmp_path)

    def failing_scanner(received_config):
        raise RuntimeError("Mock scanner failure.")

    workflow = AssessmentWorkflow(config, failing_scanner)
    result = workflow.run()

    assert result.status == AssessmentStatus.FAILED
    assert result.error == "Mock scanner failure."
    assert result.json_report is None


def test_invalid_scanner_result_is_rejected(tmp_path):
    config = create_config(tmp_path)

    workflow = AssessmentWorkflow(
        config,
        lambda received_config: "Not a findings collection",
    )

    result = workflow.run()

    assert result.status == AssessmentStatus.FAILED
    assert "FindingCollection" in result.error