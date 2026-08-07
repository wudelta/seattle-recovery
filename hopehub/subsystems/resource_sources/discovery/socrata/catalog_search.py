# ======================================================================
# FILE: hopehub/subsystems/resource_sources/discovery/socrata/catalog_search.py
# START: SOCRATA_CATALOG_SEARCH
# ======================================================================
"""Search and normalize Socrata catalog results for source discovery."""

from dataclasses import dataclass
from typing import Any, Iterable

from hopehub.subsystems.resource_sources.discovery.socrata.catalog_client import (
    SocrataCatalogClient,
)


@dataclass(frozen=True)
class SocrataDatasetCandidate:
    """One normalized dataset candidate from the Socrata catalog."""

    domain: str
    dataset_id: str
    name: str
    description: str
    category: str
    tags: tuple[str, ...]
    columns: tuple[str, ...]
    permalink: str
    license_name: str


def search_dataset_candidates(
    *,
    client: SocrataCatalogClient,
    domain: str,
    query: str,
    limit: int = 25,
) -> tuple[SocrataDatasetCandidate, ...]:
    """Return normalized dataset-only catalog matches for one query."""

    page = client.fetch_page(
        domain=domain,
        query=query,
        limit=limit,
    )

    candidates = []

    for result in page.results:
        resource = _mapping(result.get("resource"))
        resource_type = _text(resource.get("type")).lower()

        if resource_type != "dataset":
            continue

        dataset_id = _text(resource.get("id"))

        if not dataset_id:
            continue

        classification = _mapping(
            result.get("classification")
        )
        metadata = _mapping(result.get("metadata"))

        candidates.append(
            SocrataDatasetCandidate(
                domain=page.domain,
                dataset_id=dataset_id,
                name=_text(resource.get("name")),
                description=_text(
                    resource.get("description")
                ),
                category=_text(
                    classification.get("domain_category")
                ),
                tags=_text_tuple(
                    classification.get("domain_tags")
                ),
                columns=_text_tuple(
                    resource.get("columns_field_name")
                ),
                permalink=_text(result.get("permalink")),
                license_name=_text(metadata.get("license")),
            )
        )

    return tuple(candidates)


def search_multiple_queries(
    *,
    client: SocrataCatalogClient,
    domain: str,
    queries: Iterable[str],
    limit_per_query: int = 25,
) -> dict[str, tuple[SocrataDatasetCandidate, ...]]:
    """Search several terms while preserving their submitted order."""

    results = {}

    for query in queries:
        normalized_query = str(query).strip()

        if not normalized_query:
            continue

        results[normalized_query] = search_dataset_candidates(
            client=client,
            domain=domain,
            query=normalized_query,
            limit=limit_per_query,
        )

    return results


def unique_candidates(
    search_results: dict[
        str,
        tuple[SocrataDatasetCandidate, ...],
    ],
) -> tuple[SocrataDatasetCandidate, ...]:
    """Deduplicate candidates by domain and dataset identifier."""

    candidates_by_key = {}

    for candidates in search_results.values():
        for candidate in candidates:
            key = (
                candidate.domain,
                candidate.dataset_id,
            )
            candidates_by_key.setdefault(key, candidate)

    return tuple(candidates_by_key.values())


def _mapping(value: Any) -> dict[str, Any]:
    """Return a mapping-like catalog value or an empty mapping."""

    if isinstance(value, dict):
        return value

    return {}


def _text(value: Any) -> str:
    """Return stripped catalog text."""

    if value is None:
        return ""

    return str(value).strip()


def _text_tuple(value: Any) -> tuple[str, ...]:
    """Return nonempty stripped values from one catalog list."""

    if not isinstance(value, list):
        return ()

    return tuple(
        text
        for item in value
        if (text := _text(item))
    )
# ======================================================================
# END: SOCRATA_CATALOG_SEARCH
# ======================================================================