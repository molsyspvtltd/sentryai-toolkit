
"""Convert structured scanner JSON into SentryAI findings."""

import json

from toolkit.config import SentryAIConfig
from toolkit.findings import Finding, FindingCollection, Severity


def findings_from_json(
    payload: str,
    config: SentryAIConfig,
) -> FindingCollection:
    """Parse findings for a validated local DVWA configuration."""

    if not isinstance(config, SentryAIConfig):
        raise TypeError("Expected a SentryAIConfig.")

    config.validate()

    if not isinstance(payload, str):
        raise TypeError("Payload must be a JSON string.")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON payload.") from exc

    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object.")

    raw_findings = data.get("findings")

    if not isinstance(raw_findings, list):
        raise ValueError("'findings' must be a list.")

    collection = FindingCollection()

    required_fields = {
        "title",
        "description",
        "severity",
        "target",
        "recommendation",
    }

    for index, item in enumerate(raw_findings):
        if not isinstance(item, dict):
            raise ValueError(f"Finding at index {index} must be an object.")

        missing = required_fields - item.keys()
        if missing:
            raise ValueError(
                f"Finding at index {index} is missing fields: "
                f"{', '.join(sorted(missing))}"
            )

        if item["target"] != config.target_url:
            raise ValueError(
                f"Finding at index {index} has an unexpected target."
            )

        try:
            severity = Severity(item["severity"])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Finding at index {index} has invalid severity."
            ) from exc

        finding = Finding(
            title=item["title"],
            description=item["description"],
            severity=severity,
            target=item["target"],
            recommendation=item["recommendation"],
            evidence=item.get("evidence", ""),
            source=item.get("source", "SentryAI"),
        )

        collection.add(finding)

    return collection
