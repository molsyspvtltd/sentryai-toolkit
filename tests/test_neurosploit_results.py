
import json

import pytest

from toolkit.config import SentryAIConfig
from toolkit.findings import Severity
from toolkit.neurosploit_results import load_neurosploit_results


CONFIG = SentryAIConfig(
    target_url="http://127.0.0.1:4280",
    testing_scope="local-dvwa",
)


def test_load_saved_neurosploit_results(tmp_path):
    result_file = tmp_path / "findings.json"

    result_file.write_text(
        json.dumps([
            {
                "id": "saved-001",
                "title": "Synthetic saved finding",
                "severity": "High",
                "endpoint": CONFIG.target_url,
                "impact": "Synthetic impact.",
                "remediation": "Review the relevant configuration.",
            }
        ]),
        encoding="utf-8",
    )

    result = load_neurosploit_results(result_file, CONFIG)

    assert result.count() == 1
    assert result.all()[0].severity == Severity.HIGH
    assert result.all()[0].source == "NeuroSploit"


def test_missing_result_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_neurosploit_results(
            tmp_path / "findings.json",
            CONFIG,
        )


def test_wrong_filename_is_rejected(tmp_path):
    result_file = tmp_path / "other.json"
    result_file.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="findings.json"):
        load_neurosploit_results(result_file, CONFIG)


def test_invalid_saved_json_is_rejected(tmp_path):
    result_file = tmp_path / "findings.json"
    result_file.write_text("{invalid}", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_neurosploit_results(result_file, CONFIG)
def test_load_neurosploit_results_accepts_utf8_bom(tmp_path):
    from toolkit.config import SentryAIConfig
    from toolkit.neurosploit_results import load_neurosploit_results

    result_file = tmp_path / "findings.json"
    result_file.write_text(
        '[{"id":"SYN-001","title":"Test finding",'
        '"severity":"medium","endpoint":"http://127.0.0.1:4280"}]',
        encoding="utf-8-sig",
    )

    config = SentryAIConfig(
        target_url="http://127.0.0.1:4280",
        testing_scope="local-dvwa",
        output_dir=tmp_path,
    )

    findings = load_neurosploit_results(result_file, config)

    assert findings.count() == 1