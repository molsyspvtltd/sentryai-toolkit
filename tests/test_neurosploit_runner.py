
import subprocess
from unittest.mock import patch

import pytest

from toolkit.config import SentryAIConfig
from toolkit.neurosploit_runner import run_neurosploit


@pytest.fixture
def config():
    return SentryAIConfig(
        target_url="http://127.0.0.1:8080",
        testing_scope="local-dvwa",
    )


def test_runner_builds_offline_command(config, tmp_path):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()

    expected = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="Offline pipeline completed",
        stderr="",
    )

    with patch(
        "toolkit.neurosploit_runner.subprocess.run",
        return_value=expected,
    ) as mocked_run:
        result = run_neurosploit(config, executable)

    assert result.returncode == 0

    args, kwargs = mocked_run.call_args
    assert args[0] == [
        str(executable),
        "run",
        "http://127.0.0.1:8080",
        "--offline",
    ]
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True


def test_runner_rejects_external_target(config, tmp_path):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()
    config.target_url = "https://example.com"

    with patch(
        "toolkit.neurosploit_runner.subprocess.run"
    ) as mocked_run:
        with pytest.raises(ValueError):
            run_neurosploit(config, executable)

    mocked_run.assert_not_called()


def test_runner_rejects_missing_executable(config, tmp_path):
    missing = tmp_path / "missing.exe"

    with pytest.raises(FileNotFoundError):
        run_neurosploit(config, missing)


def test_runner_reports_process_failure(config, tmp_path):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()

    failure = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="",
        stderr="CLI error",
    )

    with patch(
        "toolkit.neurosploit_runner.subprocess.run",
        return_value=failure,
    ):
        with pytest.raises(RuntimeError, match="CLI error"):
            run_neurosploit(config, executable)
