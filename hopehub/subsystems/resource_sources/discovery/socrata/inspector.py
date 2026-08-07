# ======================================================================
# FILE: hopehub/subsystems/resource_sources/discovery/socrata/inspector.py
# START: SOCRATA_DATASET_INSPECTOR
# ======================================================================
"""Produce concise human-reviewable reports for Socrata datasets."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests


PROVIDER_FIELD_HINTS = {
    "provider",
    "organization",
    "agency",
    "partner",
    "clinic",
    "program",
    "name",
}

SERVICE_FIELD_HINTS = {
    "service",
    "services",
    "description",
    "program_description",
    "project_description",
}

PHONE_FIELD_HINTS = {
    "phone",
    "telephone",
    "contact_phone",
}

WEBSITE_FIELD_HINTS = {
    "website",
    "url",
    "link",
}

ADDRESS_FIELD_HINTS = {
    "address",
    "street",
    "city",
    "state",
    "zip",
    "zipcode",
    "postal_code",
    "location",
}

ELIGIBILITY_FIELD_HINTS = {
    "eligibility",
    "population",
    "audience",
    "age",
    "youth",
    "adults",
    "families",
    "older_adults",
}

GEOMETRY_FIELD_HINTS = {
    "the_geom",
    "geometry",
    "latitude",
    "longitude",
    "location",
}


@dataclass(frozen=True)
class SocrataDatasetInspection:
    """Concise evidence for deciding whether one dataset is useful."""

    dataset_id: str
    title: str
    description: str
    category: str
    rows_updated_at: str
    metadata_updated_at: str
    approximate_record_count: int | None
    column_names: tuple[str, ...]
    contains_provider_name: bool
    contains_service_description: bool
    contains_phone: bool
    contains_website: bool
    contains_address: bool
    contains_eligibility: bool
    contains_geometry: bool
    sample_records: tuple[dict[str, Any], ...]
    usefulness: str
    usefulness_reasons: tuple[str, ...]


def inspect_dataset(
    *,
    dataset_id: str,
    domain: str = "data.kingcounty.gov",
    sample_size: int = 3,
    timeout_seconds: int = 30,
) -> SocrataDatasetInspection:
    """Inspect one Socrata dataset and return a concise review object."""

    normalized_dataset_id = str(dataset_id).strip()
    normalized_domain = _normalize_domain(domain)

    if not normalized_dataset_id:
        raise ValueError(
            "dataset_id must not be empty."
        )

    if sample_size < 1:
        raise ValueError(
            "sample_size must be greater than zero."
        )

    metadata = _fetch_dataset_metadata(
        domain=normalized_domain,
        dataset_id=normalized_dataset_id,
        timeout_seconds=timeout_seconds,
    )

    columns = metadata.get("columns")

    if not isinstance(columns, list):
        columns = []

    column_names = tuple(
        field_name
        for column in columns
        if isinstance(column, dict)
        if (
            field_name := _text(
                column.get("fieldName")
                or column.get("name")
            )
        )
    )

    sample_records = _fetch_sample_records(
        domain=normalized_domain,
        dataset_id=normalized_dataset_id,
        sample_size=sample_size,
        timeout_seconds=timeout_seconds,
    )

    normalized_columns = {
        column.lower()
        for column in column_names
    }

    contains_provider_name = _contains_hint(
        normalized_columns,
        PROVIDER_FIELD_HINTS,
    )
    contains_service_description = _contains_hint(
        normalized_columns,
        SERVICE_FIELD_HINTS,
    )
    contains_phone = _contains_hint(
        normalized_columns,
        PHONE_FIELD_HINTS,
    )
    contains_website = _contains_hint(
        normalized_columns,
        WEBSITE_FIELD_HINTS,
    )
    contains_address = _contains_hint(
        normalized_columns,
        ADDRESS_FIELD_HINTS,
    )
    contains_eligibility = _contains_hint(
        normalized_columns,
        ELIGIBILITY_FIELD_HINTS,
    )
    contains_geometry = _contains_hint(
        normalized_columns,
        GEOMETRY_FIELD_HINTS,
    )

    usefulness, reasons = _assess_usefulness(
        contains_provider_name=contains_provider_name,
        contains_service_description=contains_service_description,
        contains_phone=contains_phone,
        contains_website=contains_website,
        contains_address=contains_address,
        contains_eligibility=contains_eligibility,
        contains_geometry=contains_geometry,
    )

    return SocrataDatasetInspection(
        dataset_id=normalized_dataset_id,
        title=_text(metadata.get("name")),
        description=_text(metadata.get("description")),
        category=_text(metadata.get("category")),
        rows_updated_at=_format_timestamp(
            metadata.get("rowsUpdatedAt")
        ),
        metadata_updated_at=_format_timestamp(
            metadata.get("metadataUpdatedAt")
        ),
        approximate_record_count=_optional_integer(
            metadata.get("totalRows")
        ),
        column_names=column_names,
        contains_provider_name=contains_provider_name,
        contains_service_description=(
            contains_service_description
        ),
        contains_phone=contains_phone,
        contains_website=contains_website,
        contains_address=contains_address,
        contains_eligibility=contains_eligibility,
        contains_geometry=contains_geometry,
        sample_records=sample_records,
        usefulness=usefulness,
        usefulness_reasons=reasons,
    )


def render_inspection(
    inspection: SocrataDatasetInspection,
) -> str:
    """Render one concise terminal-friendly inspection report."""

    lines = [
        "=" * 80,
        f"Dataset ID: {inspection.dataset_id}",
        f"Title: {inspection.title or '(none)'}",
        f"Category: {inspection.category or '(none)'}",
        f"Rows Updated: {inspection.rows_updated_at or '(unknown)'}",
        f"Metadata Updated: {inspection.metadata_updated_at or '(unknown)'}",
        (
            "Approximate Records: "
            f"{inspection.approximate_record_count}"
            if inspection.approximate_record_count is not None
            else "Approximate Records: (unknown)"
        ),
        "",
        "Capabilities:",
        (
            "  Provider or Program Name: "
            f"{_yes_no(inspection.contains_provider_name)}"
        ),
        (
            "  Service Description: "
            f"{_yes_no(inspection.contains_service_description)}"
        ),
        f"  Phone: {_yes_no(inspection.contains_phone)}",
        f"  Website: {_yes_no(inspection.contains_website)}",
        f"  Address: {_yes_no(inspection.contains_address)}",
        (
            "  Eligibility or Population: "
            f"{_yes_no(inspection.contains_eligibility)}"
        ),
        f"  Geometry: {_yes_no(inspection.contains_geometry)}",
        "",
        f"Assessment: {inspection.usefulness}",
    ]

    for reason in inspection.usefulness_reasons:
        lines.append(f"  - {reason}")

    lines.extend(
        [
            "",
            "Columns:",
        ]
    )

    for column in inspection.column_names:
        lines.append(f"  - {column}")

    lines.extend(
        [
            "",
            "Sample Records:",
        ]
    )

    for index, record in enumerate(
        inspection.sample_records,
        start=1,
    ):
        lines.append(f"  Record {index}:")

        for key, value in record.items():
            if str(key).startswith(":"):
                continue

            lines.append(
                f"    {key}: {_truncate_value(value)}"
            )

    if inspection.description:
        lines.extend(
            [
                "",
                "Description:",
                _truncate_text(
                    inspection.description,
                    maximum_length=500,
                ),
            ]
        )

    return "\n".join(lines)


def _fetch_dataset_metadata(
    *,
    domain: str,
    dataset_id: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Fetch authoritative metadata for one known Socrata dataset ID."""

    url = f"https://{domain}/api/views/{dataset_id}"

    try:
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f'Unable to retrieve metadata for "{dataset_id}": {exc}'
        ) from exc

    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(
            f'Dataset "{dataset_id}" metadata returned invalid JSON.'
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            f'Dataset "{dataset_id}" metadata did not return an object.'
        )

    return payload


def _fetch_sample_records(
    *,
    domain: str,
    dataset_id: str,
    sample_size: int,
    timeout_seconds: int,
) -> tuple[dict[str, Any], ...]:
    """Fetch a small sample from one Socrata dataset."""

    url = (
        f"https://{domain}/api/v3/views/"
        f"{dataset_id}/query.json"
    )

    try:
        response = requests.get(
            url,
            params={
                "pageNumber": 1,
                "pageSize": sample_size,
            },
            headers={
                "Accept": "application/json",
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f'Unable to retrieve sample rows for "{dataset_id}": {exc}'
        ) from exc

    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(
            f'Dataset "{dataset_id}" returned invalid JSON.'
        ) from exc

    if not isinstance(payload, list):
        raise RuntimeError(
            f'Dataset "{dataset_id}" did not return a list of rows.'
        )

    invalid_indexes = [
        index
        for index, row in enumerate(payload)
        if not isinstance(row, dict)
    ]

    if invalid_indexes:
        rendered_indexes = ", ".join(
            str(index)
            for index in invalid_indexes
        )
        raise RuntimeError(
            f'Dataset "{dataset_id}" returned non-object rows at '
            f"indexes: {rendered_indexes}."
        )

    return tuple(payload)


def _assess_usefulness(
    *,
    contains_provider_name: bool,
    contains_service_description: bool,
    contains_phone: bool,
    contains_website: bool,
    contains_address: bool,
    contains_eligibility: bool,
    contains_geometry: bool,
) -> tuple[str, tuple[str, ...]]:
    """Produce a conservative usefulness assessment."""

    reasons = []

    if contains_provider_name:
        reasons.append(
            "Contains a likely provider, organization, clinic, or program field."
        )

    if contains_service_description:
        reasons.append(
            "Contains a likely service-description field."
        )

    if contains_phone or contains_website:
        reasons.append(
            "Contains at least one direct contact channel."
        )

    if contains_address or contains_geometry:
        reasons.append(
            "Contains a physical location or geographic representation."
        )

    if contains_eligibility:
        reasons.append(
            "Contains likely population or eligibility information."
        )

    strong_signals = sum(
        (
            contains_provider_name,
            contains_service_description,
            contains_phone or contains_website,
            contains_address or contains_geometry,
        )
    )

    if strong_signals >= 4:
        return "HIGH-VALUE CANDIDATE", tuple(reasons)

    if strong_signals >= 2:
        return "REVIEW REQUIRED", tuple(reasons)

    return (
        "LOW-VALUE CANDIDATE",
        tuple(reasons) or (
            "The dataset schema lacks the core fields expected for a "
            "public resource record.",
        ),
    )


def _contains_hint(
    columns: set[str],
    hints: set[str],
) -> bool:
    """Return whether any column contains one of the expected hints."""

    return any(
        hint in column
        for column in columns
        for hint in hints
    )


def _normalize_domain(domain: str) -> str:
    """Validate and normalize one Socrata portal domain."""

    if not isinstance(domain, str):
        raise TypeError(
            "domain must be text."
        )

    normalized_domain = domain.strip().lower()

    if not normalized_domain:
        raise ValueError(
            "domain must not be empty."
        )

    if "://" in normalized_domain or "/" in normalized_domain:
        raise ValueError(
            "domain must be a hostname without a scheme or path."
        )

    return normalized_domain


def _text(value: Any) -> str:
    """Return stripped text."""

    if value is None:
        return ""

    return str(value).strip()


def _optional_integer(value: Any) -> int | None:
    """Return an optional integer."""

    if value in (None, ""):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _format_timestamp(value: Any) -> str:
    """Render a Socrata timestamp for human review."""

    if value in (None, ""):
        return ""

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(
                value,
            ).astimezone().isoformat()
        except (OverflowError, OSError, ValueError):
            return str(value)

    text = _text(value)

    try:
        return datetime.fromisoformat(
            text.replace("Z", "+00:00")
        ).isoformat()
    except ValueError:
        return text


def _truncate_value(value: Any) -> str:
    """Render one sample value without flooding the terminal."""

    return _truncate_text(
        _text(value),
        maximum_length=160,
    )


def _truncate_text(
    value: str,
    *,
    maximum_length: int,
) -> str:
    """Truncate text to one concise terminal line."""

    normalized = " ".join(value.split())

    if len(normalized) <= maximum_length:
        return normalized

    return normalized[: maximum_length - 3] + "..."


def _yes_no(value: bool) -> str:
    """Render one Boolean for human review."""

    return "YES" if value else "NO"
# ======================================================================
# END: SOCRATA_DATASET_INSPECTOR
# ======================================================================