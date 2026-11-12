"""Assessment workflow orchestration for SentryAI."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

from toolkit.config import SentryAIConfig
from toolkit.findings import FindingCollection
from toolkit.reporting import (
    generate_json_report,
    generate_markdown_report,
)


class AssessmentStatus(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


@dataclass
class AssessmentResult:
    """Stores the outcome of one SentryAI assessment."""

    status: AssessmentStatus
    findings: FindingCollection
    json_report: Path | None = None
    markdown_report: Path | None = None
    error: str | None = None


Scanner = Callable[[SentryAIConfig], FindingCollection]


class AssessmentWorkflow:
    """Coordinates configuration, scanning, findings, and reporting."""

    def __init__(
        self,
        config: SentryAIConfig,
        scanner: Scanner,
        output_dir: str | Path | None = None,
    ):
        if not isinstance(config, SentryAIConfig):
            raise TypeError("Expected a SentryAIConfig.")

        if not callable(scanner):
            raise TypeError("Scanner must be callable.")

        self.config = config
        self.scanner = scanner
        self.output_dir = (
            Path(output_dir)
            if output_dir is not None
            else config.output_dir
        )
        self.status = AssessmentStatus.PENDING

    def run(self) -> AssessmentResult:
        """Execute the assessment and generate reports."""

        empty_findings = FindingCollection()

        try:
            # Validate scope before allowing scanner execution.
            self.config.validate()
            self.status = AssessmentStatus.RUNNING

            findings = self.scanner(self.config)

            if not isinstance(findings, FindingCollection):
                raise TypeError(
                    "Scanner must return a FindingCollection."
                )

            json_report = generate_json_report(
                findings,
                self.output_dir,
            )

            markdown_report = generate_markdown_report(
                findings,
                self.output_dir,
            )

            self.status = AssessmentStatus.COMPLETED

            return AssessmentResult(
                status=self.status,
                findings=findings,
                json_report=json_report,
                markdown_report=markdown_report,
            )

        except Exception as exc:
            self.status = AssessmentStatus.FAILED

            return AssessmentResult(
                status=self.status,
                findings=empty_findings,
                error=str(exc),
            )