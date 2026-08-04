# ======================================================================
# FILE: hopehub/subsystems/resource_sources/king_county_211/download_behavioral_health_dataset.py
# START: KING_COUNTY_211_BEHAVIORAL_HEALTH_PROVIDER_DOWNLOAD
# ======================================================================
"""Download the raw King County behavioral-health provider dataset."""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import environ
import requests


DATASET_ID = "sep3-3pj3"
DATASET_NAME = "king_county_mental_health_and_sud_providers"
DATASET_URL = (
    f"https://data.kingcounty.gov/api/v3/views/{DATASET_ID}/query.json"
)
TOKEN_ENV_VAR = "KING_COUNTY_211_APP_TOKEN"
DEFAULT_PAGE_SIZE = 200
REQUEST_TIMEOUT_SECONDS = 30

PROJECT_ROOT = Path(__file__).resolve().parents[4]
ENV_FILE = PROJECT_ROOT / ".env"


def load_app_token() -> str:
    """Load the Socrata application token without exposing it in output."""

    if ENV_FILE.exists():
        environ.Env.read_env(ENV_FILE)

    app_token = os.getenv(TOKEN_ENV_VAR, "").strip()

    if not app_token:
        raise RuntimeError(
            f"Missing required environment variable: {TOKEN_ENV_VAR}"
        )

    return app_token


def fetch_dataset(app_token: str, page_size: int) -> Any:
    """Fetch and return the unmodified JSON response."""

    response = requests.get(
        DATASET_URL,
        params={
            "pageNumber": 1,
            "pageSize": page_size,
            "app_token": app_token,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(
            "King County returned a response that was not valid JSON."
        ) from exc


def save_raw_snapshot(payload: Any, output_directory: Path) -> Path:
    """Save the exact decoded JSON payload without normalization."""

    if not output_directory.exists():
        raise FileNotFoundError(
            "The output directory does not exist: "
            f"{output_directory}"
        )

    if not output_directory.is_dir():
        raise NotADirectoryError(
            f"The output path is not a directory: {output_directory}"
        )

    timestamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    output_path = output_directory / (
        f"{DATASET_NAME}_{timestamp}.json"
    )

    with output_path.open("w", encoding="utf-8") as snapshot_file:
        json.dump(
            payload,
            snapshot_file,
            indent=2,
            ensure_ascii=False,
        )
        snapshot_file.write("\n")

    return output_path


def describe_payload(payload: Any, page_size: int) -> None:
    """Print minimal acquisition results without interpreting the schema."""

    print(f"Dataset ID: {DATASET_ID}")
    print(f"Response type: {type(payload).__name__}")

    if isinstance(payload, list):
        record_count = len(payload)
        print(f"Records downloaded: {record_count}")

        if record_count >= page_size:
            print(
                "WARNING: The response reached the configured page size. "
                "Additional pages may exist."
            )
        return

    if isinstance(payload, dict):
        print(f"Top-level keys: {', '.join(sorted(payload.keys()))}")
        return

    print(
        "WARNING: The response was valid JSON but did not contain a "
        "top-level list or object."
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Download the raw King County mental-health and "
            "substance-use-disorder provider dataset."
        )
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help=(
            "Existing directory where the raw JSON snapshot will be saved."
        ),
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=(
            "Number of records requested from the API. "
            f"Default: {DEFAULT_PAGE_SIZE}."
        ),
    )

    arguments = parser.parse_args()

    if arguments.page_size < 1:
        parser.error("--page-size must be greater than zero.")

    return arguments


def main() -> None:
    """Download one raw dataset snapshot."""

    arguments = parse_arguments()
    app_token = load_app_token()

    print(f"Downloading King County dataset {DATASET_ID}...")

    payload = fetch_dataset(
        app_token=app_token,
        page_size=arguments.page_size,
    )
    output_path = save_raw_snapshot(
        payload=payload,
        output_directory=arguments.output_dir,
    )

    describe_payload(payload, arguments.page_size)
    print(f"Raw snapshot saved to: {output_path}")


if __name__ == "__main__":
    main()
# ======================================================================
# END: KING_COUNTY_211_BEHAVIORAL_HEALTH_PROVIDER_DOWNLOAD
# ======================================================================