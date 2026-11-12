
"""JSON and Markdown report generation for SentryAI."""

import json
from datetime import datetime, timezone
from pathlib import Path

from toolkit.findings import FindingCollection


def generate_json_report(
    collection: FindingCollection,
    output_dir: str | Path = "reports",
) -> Path:
    """Export assessment findings as a JSON report."""

    if not isinstance(collection, FindingCollection):
        raise TypeError("Expected a FindingCollection.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = {
        "project": "SentryAI",
        "report_type": "Security Assessment",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_findings": collection.count(),
        "severity_summary": collection.summary(),
        "findings": [
            finding.to_dict()
            for finding in collection.all()
        ],
    }

    file_path = output_path / "sentryai_report.json"

    file_path.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8",
    )

    return file_path


def generate_markdown_report(
    collection: FindingCollection,
    output_dir: str | Path = "reports",
) -> Path:
    """Generate a readable Markdown assessment report."""

    if not isinstance(collection, FindingCollection):
        raise TypeError("Expected a FindingCollection.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    lines = [
        "# SentryAI Security Assessment Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Assessment Summary",
        "",
        f"**Total Findings:** {collection.count()}",
        "",
        "### Severity Distribution",
        "",
    ]

    for severity, count in collection.summary().items():
        lines.append(f"- **{severity}:** {count}")

    lines.extend(["", "## Detailed Findings", ""])

    if not collection.all():
        lines.append("No findings were recorded.")
    else:
        for index, finding in enumerate(collection.all(), 1):
            lines.extend([
                f"### {index}. {finding.title}",
                "",
                f"- **ID:** {finding.finding_id}",
                f"- **Severity:** {finding.severity.value}",
                f"- **Target:** {finding.target}",
                f"- **Source:** {finding.source}",
                "",
                "**Description**",
                "",
                finding.description,
                "",
                "**Evidence**",
                "",
                finding.evidence or "No evidence recorded.",
                "",
                "**Recommendation**",
                "",
                finding.recommendation,
                "",
                "---",
                "",
            ])

    file_path = output_path / "sentryai_report.md"

    file_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return file_path
