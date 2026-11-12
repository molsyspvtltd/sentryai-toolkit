"""Offline demonstration of the SentryAI assessment workflow."""

from pathlib import Path

from toolkit.assessment import AssessmentWorkflow
from toolkit.config import SentryAIConfig
from toolkit.result_adapter import findings_from_json


def main():
    project_dir = Path(__file__).resolve().parent
    sample_file = project_dir / "examples" / "sample_scan_results.json"

    if not sample_file.is_file():
        print("Sample results file not found.")
        return 1

    config = SentryAIConfig(
        target_url="http://127.0.0.1:4280",
        testing_scope="local-dvwa",
        output_dir=project_dir / "reports",
    )

    payload = sample_file.read_text(encoding="utf-8")

    def offline_scanner(received_config):
        return findings_from_json(payload, received_config)

    workflow = AssessmentWorkflow(
        config=config,
        scanner=offline_scanner,
        output_dir=config.output_dir,
    )

    result = workflow.run()

    print("\n========== SENTRYAI DEMO ==========")
    print(f"Assessment status: {result.status.value}")

    if result.status.value != "Completed":
        print(f"Error: {result.error}")
        return 1

    print(f"Total sample findings: {result.findings.count()}")

    print("\nSeverity summary:")
    for severity, count in result.findings.summary().items():
        print(f"{severity}: {count}")

    print("\nGenerated reports:")
    print(f"JSON: {result.json_report}")
    print(f"Markdown: {result.markdown_report}")

    print("\nNote: These are synthetic demonstration findings.")
    print("No live security scan was performed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())