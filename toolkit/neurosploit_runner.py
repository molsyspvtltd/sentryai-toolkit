
"""Safe CLI integration for checking the NeuroSploit installation."""

import os
import shutil
import subprocess
from pathlib import Path

from toolkit.config import SentryAIConfig


def resolve_neurosploit_path(
    executable_path: str | Path | None = None,
) -> Path:
    """Find NeuroSploit using an explicit path, environment variable, or PATH."""

    candidate = executable_path or os.environ.get("NEUROSPLOIT_PATH")

    if candidate:
        executable = Path(candidate).expanduser()

        if not executable.is_file():
            raise FileNotFoundError(
                f"NeuroSploit executable not found: {executable}"
            )

        return executable.resolve()

    for command in ("neurosploit", "neurosploit.exe"):
        discovered = shutil.which(command)

        if discovered:
            return Path(discovered).resolve()

    raise FileNotFoundError(
        "NeuroSploit not found. Set NEUROSPLOIT_PATH "
        "or add it to your system PATH."
    )


def check_neurosploit(
    config: SentryAIConfig,
    executable_path: str | Path | None = None,
    timeout: int = 30,
) -> dict[str, str]:
    """Verify the local target configuration and NeuroSploit CLI.

    This function only checks the CLI version and agent inventory.
    It does not launch a security scan.
    """

    config.validate()
    executable = resolve_neurosploit_path(executable_path)

    checks = {}

    commands = {
        "version": [str(executable), "--version"],
        "agents": [str(executable), "agents"],
    }

    for name, command in commands.items():
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(
                f"NeuroSploit {name} check timed out."
            ) from exc

        if result.returncode != 0:
            raise RuntimeError(
                f"NeuroSploit {name} check failed: {result.stderr}"
            )

        checks[name] = result.stdout.strip()

    return checks


