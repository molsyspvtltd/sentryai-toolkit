
"""Finding models and validation for SentryAI."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"


@dataclass
class Finding:
    """Represents one security finding from an assessment."""

    title: str
    description: str
    severity: Severity
    target: str
    recommendation: str
    evidence: str = ""
    source: str = "SentryAI"
    finding_id: str = ""
    discovered_at: str = ""

    def __post_init__(self):
        if not self.finding_id:
            self.finding_id = str(uuid4())

        if not self.discovered_at:
            self.discovered_at = datetime.now(
                timezone.utc
            ).isoformat()

        self.validate()

    def validate(self):
        """Validate finding fields before accepting a finding."""

        required_fields = {
            "title": self.title,
            "description": self.description,
            "target": self.target,
            "recommendation": self.recommendation,
            "source": self.source,
        }

        for field, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Finding {field} cannot be empty."
                )

        if not isinstance(self.severity, Severity):
            raise ValueError("Invalid finding severity.")

        if not isinstance(self.evidence, str):
            raise ValueError("Evidence must be a string.")

    def to_dict(self):
        """Convert the finding into a JSON-compatible dictionary."""

        data = asdict(self)
        data["severity"] = self.severity.value
        return data


class FindingCollection:
    """Stores and manages findings from an assessment."""

    def __init__(self):
        self._findings = []

    def add(self, finding: Finding):
        if not isinstance(finding, Finding):
            raise TypeError("Only Finding objects can be added.")

        if any(
            item.finding_id == finding.finding_id
            for item in self._findings
        ):
            raise ValueError("Duplicate finding ID.")

        self._findings.append(finding)

    def all(self):
        return list(self._findings)

    def count(self):
        return len(self._findings)

    def by_severity(self, severity: Severity):
        if not isinstance(severity, Severity):
            raise ValueError("Invalid severity filter.")

        return [
            finding
            for finding in self._findings
            if finding.severity == severity
        ]

    def summary(self):
        """Return the number of findings in each severity category."""

        return {
            severity.value: len(self.by_severity(severity))
            for severity in Severity
        }
