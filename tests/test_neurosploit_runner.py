
"""Tests for safe NeuroSploit CLI verification."""

import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from toolkit.config import SentryAIConfig
from toolkit.neurosploit_runner import (
    check_neurosploit,
    resolve_neurosploit_path,
)


@pytest.fixture
def config():
    return SentryAIConfig(
        target_url="http://127.0.0.1:4280",
        testing_scope="local-dvwa",
    )


def test_resolve_explicit_executable_path(tmp_path):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()

    result = resolve_neurosploit_path(executable)

    assert result == executable.resolve()


def test_resolve_executable_from_environment(tmp_path, monkeypatch):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()

    monkeypatch.setenv("NEUROSPLOIT_PATH", str(executable))

    result = resolve_neurosploit_path()

    assert result == executable.resolve()


def test_resolve_executable_from_path(monkeypatch):
    monkeypatch.delenv("NEUROSPLOIT_PATH", raising=False)
    monkeypatch.setattr(
        "toolkit.neurosploit_runner.shutil.which",
        lambda command: "C:/tools/neurosploit.exe"
        if command == "neurosploit"
        else None,
    )

    result = resolve_neurosploit_path()

    assert result == Path("C:/tools/neurosploit.exe").resolve()


def test_missing_executable_raises_error(monkeypatch):
    monkeypatch.delenv("NEUROSPLOIT_PATH", raising=False)
    monkeypatch.setattr(
        "toolkit.neurosploit_runner.shutil.which",
        lambda command: None,
    )

    with pytest.raises(FileNotFoundError, match="NeuroSploit not found"):
        resolve_neurosploit_path()


def test_successful_cli_checks(config, tmp_path, monkeypatch):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()

    responses = [
        Mock(returncode=0, stdout="neurosploit 4.4.0", stderr=""),
        Mock(returncode=0, stdout='{"total":485}', stderr=""),
    ]

    mocked_run = Mock(side_effect=responses)
    monkeypatch.setattr(
        "toolkit.neurosploit_runner.subprocess.run",
        mocked_run,
    )

    result = check_neurosploit(config, executable)

    assert result["version"] == "neurosploit 4.4.0"
    assert result["agents"] == '{"total":485}'
    assert mocked_run.call_count == 2

    commands = [
        call.args[0] for call in mocked_run.call_args_list
    ]
    assert commands[0] == [str(executable), "--version"]
    assert commands[1] == [str(executable), "agents"]


def test_external_target_is_rejected(config, tmp_path, monkeypatch):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()
    config.target_url = "https://example.com"

    mocked_run = Mock()
    monkeypatch.setattr(
        "toolkit.neurosploit_runner.subprocess.run",
        mocked_run,
    )

    with pytest.raises(ValueError):
        check_neurosploit(config, executable)

    mocked_run.assert_not_called()


def test_cli_failure_raises_runtime_error(config, tmp_path, monkeypatch):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()

    mocked_run = Mock(
        return_value=Mock(
            returncode=1,
            stdout="",
            stderr="CLI error",
        )
    )
    monkeypatch.setattr(
        "toolkit.neurosploit_runner.subprocess.run",
        mocked_run,
    )

    with pytest.raises(RuntimeError, match="CLI error"):
        check_neurosploit(config, executable)


def test_cli_timeout_raises_timeout_error(config, tmp_path, monkeypatch):
    executable = tmp_path / "neurosploit.exe"
    executable.touch()

    mocked_run = Mock(
        side_effect=subprocess.TimeoutExpired(
            cmd="neurosploit",
            timeout=30,
        )
    )
    monkeypatch.setattr(
        "toolkit.neurosploit_runner.subprocess.run",
        mocked_run,
    )

    with pytest.raises(TimeoutError, match="version check timed out"):
        check_neurosploit(config, executable)





