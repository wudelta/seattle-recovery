# ======================================================================
# FILE: hopehub/subsystems/resource_sources/discovery/socrata/candidate_report.py
# START: SOCRATA_CANDIDATE_REPORT
# ======================================================================
"""Render durable candidate reports from normalized Socrata searches."""

import json
from dataclasses import asdict
from pathlib import Path

from hopehub.subsystems.resource_sources.discovery.socrata.catalog_client import (
    SocrataCatalogClient,
)
from hopehub.subsystems.resource_sources.discovery.socrata.catalog_search import (
    SocrataDatasetCandidate,
    search_multiple_queries,
    unique_candidates,
)


DEFAULT_QUERIES = (
    "shelter",
    "homeless",
    "housing assistance",
    "food assistance",
    "food bank",
    "human services",
    "health clinic",
    "mental health",
    "substance use",
    "recovery",
    "social services",
)


def build_candidate_report(
    *,
    client: SocrataCatalogClient,
    domain: str,
    queries: tuple[str, ...] = DEFAULT_QUERIES,
    limit_per_query: int = 25,
) -> dict:
    """Build one deterministic candidate report for a Socrata domain."""

    search_results = search_multiple_queries(
        client=client,
        domain=domain,
        queries=queries,
        limit_per_query=limit_per_query,
    )
    candidates = unique_candidates(search_results)

    matched_queries = {
        candidate.dataset_id: tuple(
            query
            for query, query_candidates in search_results.items()
            if any(
                item.dataset_id == candidate.dataset_id
                for item in query_candidates
            )
        )
        for candidate in candidates
    }

    return {
        "domain": domain,
        "queries": list(search_results),
        "query_count": len(search_results),
        "candidate_count": len(candidates),
        "candidates": [
            _serialize_candidate(
                candidate,
                matched_queries[candidate.dataset_id],
            )
            for candidate in candidates
        ],
    }


def write_candidate_report(
    report: dict,
    output_path: Path,
) -> None:
    """Write one candidate report as formatted JSON."""

    if not output_path.parent.exists():
        raise FileNotFoundError(
            "The output directory does not exist: "
            f"{output_path.parent}"
        )

    if not output_path.parent.is_dir():
        raise NotADirectoryError(
            "The output parent is not a directory: "
            f"{output_path.parent}"
        )

    with output_path.open("w", encoding="utf-8") as report_file:
        json.dump(
            report,
            report_file,
            indent=2,
            ensure_ascii=False,
        )
        report_file.write("\n")


def _serialize_candidate(
    candidate: SocrataDatasetCandidate,
    matched_queries: tuple[str, ...],
) -> dict:
    """Serialize one candidate with its discovery evidence."""

    payload = asdict(candidate)
    payload["matched_queries"] = list(matched_queries)

    return payload
# ======================================================================
# END: SOCRATA_CANDIDATE_REPORT
# ======================================================================