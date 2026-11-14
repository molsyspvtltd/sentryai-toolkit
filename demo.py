
"""Import saved scanner JSON and generate SentryAI reports."""

import argparse
from pathlib import Path

from toolkit.assessment import AssessmentWorkflow
from toolkit.config import SentryAIConfig
from toolkit.result_adapter import findings_from_json


def main():
    project_dir = Path(__file__).resolve().parent
    sample_file = project_dir / "examples" / "sample_scan_results.json"

    parser = argparse.ArgumentParser(
        description="Import saved JSON findings into SentryAI."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=str(sample_file),
        help="Path to a saved SentryAI-compatible scanner JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(project_dir / "reports"),
        help="Directory for generated reports.",
    )

    args = parser.parse_args()

    input_file = Path(args.input_file).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_file.is_file():
        print(f"Input file not found: {input_file}")
        return 1

    try:
        payload = input_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Could not read input file: {exc}")
        return 1

    config = SentryAIConfig(
        target_url="http://127.0.0.1:4280",
        testing_scope="local-dvwa",
        output_dir=output_dir,
    )

    def saved_results_importer(received_config):
        return findings_from_json(payload, received_config)

    workflow = AssessmentWorkflow(
        config=config,
        scanner=saved_results_importer,
        output_dir=output_dir,
    )

    result = workflow.run()

    print("\n========== SENTRYAI IMPORT ==========")
    print(f"Input file: {input_file}")
    print(f"Assessment status: {result.status.value}")

    if result.status.value != "Completed":
        print(f"Import failed: {result.error}")
        return 1

    print(f"Imported findings: {result.findings.count()}")

    print("\nSeverity summary:")
    for severity, count in result.findings.summary().items():
        print(f"{severity}: {count}")

    print("\nGenerated reports:")
    print(f"JSON: {result.json_report}")
    print(f"Markdown: {result.markdown_report}")

    if input_file == sample_file.resolve():
        print("\nNote: The default sample contains synthetic findings.")
    else:
        print("\nNote: Results were imported from a saved JSON file.")
        print("Verify the source and assessment evidence separately.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
