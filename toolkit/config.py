
"""Configuration loading and validation for SentryAI."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class SentryAIConfig:
    """Settings required for the initial SentryAI workflow."""

    target_url: str
    testing_scope: str
    output_dir: Path = Path("reports")
    log_level: str = "INFO"

    def validate(self) -> None:
        """Reject invalid settings before an assessment can start."""

        if self.testing_scope != "local-dvwa":
            raise ValueError(
                "Only the approved local-dvwa testing scope is permitted."
            )

        parsed_url = urlparse(self.target_url)

        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError("Target URL must use HTTP or HTTPS.")

        if not parsed_url.hostname:
            raise ValueError("Target URL must include a hostname.")

        hostname = parsed_url.hostname.lower()

        if hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError(
                "Only a local DVWA target is permitted."
            )

        if self.log_level.upper() not in {
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        }:
            raise ValueError("Invalid log level.")

