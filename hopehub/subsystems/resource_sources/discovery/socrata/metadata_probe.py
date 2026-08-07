# ======================================================================
# FILE: hopehub/subsystems/resource_sources/king_county_211/probe_dataset_metadata.py
# START: KING_COUNTY_211_DATASET_METADATA_PROBE
# ======================================================================
"""Inspect authoritative metadata for registered King County datasets."""

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import environ
import requests

from hopehub.subsystems.resource_sources.registries.king_county import (
    DATASETS,
    KING_COUNTY_APP_TOKEN_ENV_VAR,
    KingCountyDataset,
)


REQUEST_TIMEOUT_SECONDS = 30

PROJECT_ROOT = Path(__file__).resolve().parents[4]
ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class DatasetMetadataResult:
    """Normalized metadata-probe result for one candidate dataset."""

    key: str
    dataset_id: str
    expected_name: str
    verification_status: str
    probe_status: str
    actual_title: str
    actual_description: str
    category: str
    attribution: str
    rows_updated_at: int | None
    metadata_updated_at: int | None
    column_count: int
    error: str


def load_app_token() -> str:
    """Load the optional Socrata application token."""

    if ENV_FILE.exists():
        environ.Env.read_env(ENV_FILE)

    return os.getenv(
        KING_COUNTY_APP_TOKEN_ENV_VAR,
        "",
    ).strip()


def fetch_dataset_metadata(
    dataset: KingCountyDataset,
    app_token: str,
) -> dict[str, Any]:
    """Fetch the unmodified Socrata metadata object for one dataset."""

    headers = {
        "Accept": "application/json",
    }

    if app_token:
        headers["X-App-Token"] = app_token

    response = requests.get(
        dataset.metadata_url,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(
            "King County returned metadata that was not valid JSON."
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            "King County returned metadata without a top-level object."
        )

    return payload


def normalize_dataset_metadata(
    dataset: KingCountyDataset,
    payload: dict[str, Any],
) -> DatasetMetadataResult:
    """Normalize only the metadata needed for source verification."""

    metadata = payload.get("metadata")

    if not isinstance(metadata, dict):
        metadata = {}

    custom_fields = metadata.get("custom_fields")

    if not isinstance(custom_fields, dict):
        custom_fields = {}

    columns = payload.get("columns")

    if not isinstance(columns, list):
        columns = []

    return DatasetMetadataResult(
        key=dataset.key,
        dataset_id=dataset.dataset_id,
        expected_name=dataset.expected_name,
        verification_status=dataset.verification_status.value,
        probe_status="RETRIEVED",
        actual_title=_text(payload.get("name")),
        actual_description=_text(payload.get("description")),
        category=_text(payload.get("category")),
        attribution=_text(payload.get("attribution")),
        rows_updated_at=_optional_integer(
            payload.get("rowsUpdatedAt")
        ),
        metadata_updated_at=_optional_integer(
            payload.get("metadataUpdatedAt")
        ),
        column_count=len(columns),
        error="",
    )


def probe_dataset(
    dataset: KingCountyDataset,
    app_token: str,
) -> DatasetMetadataResult:
    """Retrieve one dataset's metadata without stopping the full probe."""

    try:
        payload = fetch_dataset_metadata(
            dataset=dataset,
            app_token=app_token,
        )
        return normalize_dataset_metadata(dataset, payload)
    except (
        requests.RequestException,
        RuntimeError,
    ) as exc:
        return DatasetMetadataResult(
            key=dataset.key,
            dataset_id=dataset.dataset_id,
            expected_name=dataset.expected_name,
            verification_status=dataset.verification_status.value,
            probe_status="FAILED",
            actual_title="",
            actual_description="",
            category="",
            attribution="",
            rows_updated_at=None,
            metadata_updated_at=None,
            column_count=0,
            error=str(exc),
        )


def probe_all_datasets(
    app_token: str,
) -> list[DatasetMetadataResult]:
    """Probe every registered dataset in deterministic registry order."""

    return [
        probe_dataset(
            dataset=dataset,
            app_token=app_token,
        )
        for dataset in DATASETS
    ]


def write_report(
    results: list[DatasetMetadataResult],
    output_path: Path,
) -> None:
    """Write one deterministic JSON metadata report."""

    parent = output_path.parent

    if not parent.exists():
        raise FileNotFoundError(
            f"The output directory does not exist: {parent}"
        )

    if not parent.is_dir():
        raise NotADirectoryError(
            f"The output parent is not a directory: {parent}"
        )

    payload = [
        asdict(result)
        for result in results
    ]

    with output_path.open("w", encoding="utf-8") as report_file:
        json.dump(
            payload,
            report_file,
            indent=2,
            ensure_ascii=False,
        )
        report_file.write("\n")


def print_report(
    results: list[DatasetMetadataResult],
) -> None:
    """Print one concise line per dataset and a final count summary."""

    retrieved = 0
    failed = 0

    for result in results:
        if result.probe_status == "RETRIEVED":
            retrieved += 1
        else:
            failed += 1

        title = result.actual_title or result.expected_name

        print(
            f"{result.dataset_id} "
            f"{result.probe_status:<9} "
            f"columns={result.column_count:<3} "
            f"title={title}"
        )

        if result.error:
            print(f"  error={result.error}")

    print(
        "PROBE COMPLETE: "
        f"datasets={len(results)} "
        f"retrieved={retrieved} "
        f"failed={failed}"
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Retrieve authoritative metadata for every registered "
            "King County resource dataset."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Optional JSON report path. Its parent directory must "
            "already exist."
        ),
    )

    return parser.parse_args()


def _text(value: Any) -> str:
    """Return stripped text for a metadata value."""

    if value is None:
        return ""

    return str(value).strip()


def _optional_integer(value: Any) -> int | None:
    """Return an integer metadata value when one is available."""

    if value in (None, ""):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    """Probe all registered candidate datasets."""

    arguments = parse_arguments()
    app_token = load_app_token()
    results = probe_all_datasets(app_token)

    print_report(results)

    if arguments.output:
        write_report(
            results=results,
            output_path=arguments.output,
        )
        print(f"Metadata report saved to: {arguments.output}")


if __name__ == "__main__":
    main()
# ======================================================================
# END: KING_COUNTY_211_DATASET_METADATA_PROBE
# ======================================================================