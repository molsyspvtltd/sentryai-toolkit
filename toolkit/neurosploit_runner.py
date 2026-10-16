
"""Safe subprocess wrapper for the NeuroSploit CLI."""

import subprocess
from pathlib import Path

from toolkit.config import SentryAIConfig


def run_neurosploit(
    config: SentryAIConfig,
    executable_path: str | Path,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    """Run NeuroSploit in offline mode against an approved local target."""

    # Reject an unapproved target before launching another process.
    config.validate()

    executable = Path(executable_path)

    if not executable.is_file():
        raise FileNotFoundError(
            f"NeuroSploit executable not found: {executable}"
        )

    command = [
        str(executable),
        "run",
        config.target_url,
        "--offline",
    ]

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
            f"NeuroSploit exceeded the {timeout}-second timeout."
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"NeuroSploit failed with exit code {result.returncode}: "
            f"{result.stderr}"
        )

    return result
