
"""Read saved NeuroSploit findings without executing the scanner."""

from pathlib import Path

from toolkit.config import SentryAIConfig
from toolkit.findings import FindingCollection
from toolkit.result_adapter import findings_from_json


def load_neurosploit_results(
    result_file: str | Path,
    config: SentryAIConfig,
) -> FindingCollection:
    """Load and convert a saved NeuroSploit findings.json file."""

    path = Path(result_file)

    if not path.exists():
        raise FileNotFoundError(
            f"NeuroSploit result file not found: {path}"
        )

    if not path.is_file():
        raise ValueError("Result path must point to a file.")

    if path.name.lower() != "findings.json":
        raise ValueError(
            "Expected a NeuroSploit findings.json file."
        )

    try:
        payload = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "NeuroSploit result file must use UTF-8 encoding."
        ) from exc

    return findings_from_json(payload, config)
