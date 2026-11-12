
import json

from toolkit.assessment import AssessmentStatus, AssessmentWorkflow
from toolkit.config import SentryAIConfig
from toolkit.result_adapter import findings_from_json


def test_result_adapter_integrates_with_assessment_workflow(tmp_path):
    config = SentryAIConfig(
        target_url="http://127.0.0.1:4280",
        testing_scope="local-dvwa",
    )

    payload = json.dumps({
        "findings": [
            {
                "title": "Synthetic sample finding",
                "description": "Test data for workflow integration.",
                "severity": "Medium",
                "target": config.target_url,
                "recommendation": "Review the application configuration.",
                "evidence": "Synthetic evidence only",
                "source": "SampleData",
            }
        ]
    })

    scanner_calls = []

    def scanner(received_config):
        scanner_calls.append(received_config)
        return findings_from_json(payload, received_config)

    workflow = AssessmentWorkflow(
        config=config,
        scanner=scanner,
        output_dir=tmp_path,
    )

    result = workflow.run()

    assert result.status == AssessmentStatus.COMPLETED
    assert result.findings.count() == 1
    assert result.findings.all()[0].target == config.target_url
    assert result.json_report.exists()
    assert result.markdown_report.exists()
    assert len(scanner_calls) == 1
