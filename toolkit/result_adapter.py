
"""Convert SentryAI and NeuroSploit JSON results into SentryAI findings."""

import json

from toolkit.config import SentryAIConfig
from toolkit.findings import Finding, FindingCollection, Severity


def _parse_severity(value, index):
    """Convert supported scanner severity labels into SentryAI severity."""

    if not isinstance(value, str):
        raise ValueError(
            f"Finding at index {index} has invalid severity."
        )

    severity_map = {
        "critical": Severity.CRITICAL,
        "high": Severity.HIGH,
        "medium": Severity.MEDIUM,
        "low": Severity.LOW,
        "info": Severity.INFORMATIONAL,
        "informational": Severity.INFORMATIONAL,
    }

    severity = severity_map.get(value.strip().lower())

    if severity is None:
        raise ValueError(
            f"Finding at index {index} has invalid severity."
        )

    return severity


def _parse_sentryai_findings(raw_findings, config):
    """Preserve compatibility with the existing SentryAI JSON format."""

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
            raise ValueError(
                f"Finding at index {index} must be an object."
            )

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

        finding = Finding(
            title=item["title"],
            description=item["description"],
            severity=_parse_severity(item["severity"], index),
            target=item["target"],
            recommendation=item["recommendation"],
            evidence=item.get("evidence", ""),
            source=item.get("source", "SentryAI"),
        )

        collection.add(finding)

    return collection


def _parse_neurosploit_findings(raw_findings, config):
    """Convert NeuroSploit's native JSON array into SentryAI findings."""

    collection = FindingCollection()

    for index, item in enumerate(raw_findings):
        if not isinstance(item, dict):
            raise ValueError(
                f"Finding at index {index} must be an object."
            )

        endpoint = item.get("endpoint") or config.target_url

        if endpoint != config.target_url:
            raise ValueError(
                f"Finding at index {index} has an unexpected target."
            )

        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(
                f"Finding at index {index} has an invalid title."
            )

        severity = _parse_severity(item.get("severity"), index)

        impact = item.get("impact")
        description = (
            impact.strip()
            if isinstance(impact, str) and impact.strip()
            else "NeuroSploit reported this finding, but no impact "
                 "description was provided."
        )

        remediation = item.get("remediation")
        recommendation = (
            remediation.strip()
            if isinstance(remediation, str) and remediation.strip()
            else "Manually review this finding and determine "
                 "an appropriate remediation."
        )

        evidence = item.get("evidence", "")
        if not isinstance(evidence, str):
            evidence = ""

        # Preserve useful scanner context without copying sensitive
        # fields such as secrets, payloads, or reproduction steps.
        metadata = []

        for field in ("agent", "cwe", "cvss", "votes", "review_status"):
            value = item.get(field)
            if isinstance(value, str) and value.strip():
                metadata.append(f"{field.upper()}: {value.strip()}")

        if isinstance(item.get("validated"), bool):
            metadata.append(
                f"Validated: {item['validated']}"
            )

        confidence = item.get("confidence")
        if isinstance(confidence, (int, float)) and not isinstance(
            confidence, bool
        ):
            metadata.append(f"Confidence: {confidence}")

        if metadata:
            evidence = "\n".join(
                part for part in [evidence, *metadata] if part
            )

        finding = Finding(
            title=title,
            description=description,
            severity=severity,
            target=endpoint,
            recommendation=recommendation,
            evidence=evidence,
            source="NeuroSploit",
            finding_id=item.get("id", ""),
        )

        collection.add(finding)

    return collection


def findings_from_json(
    payload: str,
    config: SentryAIConfig,
) -> FindingCollection:
    """Parse SentryAI or native NeuroSploit JSON for local DVWA."""

    if not isinstance(config, SentryAIConfig):
        raise TypeError("Expected a SentryAIConfig.")

    config.validate()

    if not isinstance(payload, str):
        raise TypeError("Payload must be a JSON string.")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON payload.") from exc

    # NeuroSploit native format: a JSON array of findings.
    if isinstance(data, list):
        return _parse_neurosploit_findings(data, config)

    # Existing SentryAI format: an object containing "findings".
    if isinstance(data, dict):
        raw_findings = data.get("findings")

        if not isinstance(raw_findings, list):
            raise ValueError("'findings' must be a list.")

        return _parse_sentryai_findings(raw_findings, config)

    raise ValueError("JSON root must be an object or an array.")
