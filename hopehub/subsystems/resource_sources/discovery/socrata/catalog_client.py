# ======================================================================
# FILE: hopehub/subsystems/resource_sources/discovery/socrata/catalog_client.py
# START: SOCRATA_CATALOG_CLIENT
# ======================================================================
"""Retrieve public asset metadata from the Socrata Discovery API."""

from dataclasses import dataclass
from typing import Any

import requests


SOCRATA_CATALOG_URL = "https://api.us.socrata.com/api/catalog/v1"
DEFAULT_PAGE_SIZE = 100
REQUEST_TIMEOUT_SECONDS = 30


class SocrataCatalogError(RuntimeError):
    """Raised when the Socrata catalog cannot produce a usable response."""


@dataclass(frozen=True)
class SocrataCatalogPage:
    """One validated page returned by the Socrata Discovery API."""

    domain: str
    offset: int
    limit: int
    result_set_size: int
    results: tuple[dict[str, Any], ...]


class SocrataCatalogClient:
    """Retrieve paged catalog results for one Socrata-hosted domain."""

    def __init__(
        self,
        *,
        timeout_seconds: int = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        if timeout_seconds < 1:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )

        self.timeout_seconds = timeout_seconds

    def fetch_page(
        self,
        *,
        domain: str,
        offset: int = 0,
        limit: int = DEFAULT_PAGE_SIZE,
        query: str = "",
    ) -> SocrataCatalogPage:
        """Retrieve one catalog page for a Socrata domain."""

        normalized_domain = self._normalize_domain(domain)

        if offset < 0:
            raise ValueError(
                "offset must be zero or greater."
            )

        if limit < 1:
            raise ValueError(
                "limit must be greater than zero."
            )

        params: dict[str, Any] = {
            "domains": normalized_domain,
            "offset": offset,
            "limit": limit,
        }

        normalized_query = query.strip()

        if normalized_query:
            params["q"] = normalized_query

        payload = self._request(params)

        result_set_size = payload.get("resultSetSize")

        if (
            isinstance(result_set_size, bool)
            or not isinstance(result_set_size, int)
            or result_set_size < 0
        ):
            raise SocrataCatalogError(
                "Socrata catalog resultSetSize must be a "
                "non-negative integer."
            )

        raw_results = payload.get("results")

        if not isinstance(raw_results, list):
            raise SocrataCatalogError(
                "Socrata catalog results must be a list."
            )

        invalid_indexes = [
            index
            for index, result in enumerate(raw_results)
            if not isinstance(result, dict)
        ]

        if invalid_indexes:
            rendered_indexes = ", ".join(
                str(index)
                for index in invalid_indexes
            )
            raise SocrataCatalogError(
                "Socrata catalog returned non-object results at "
                f"indexes: {rendered_indexes}."
            )

        return SocrataCatalogPage(
            domain=normalized_domain,
            offset=offset,
            limit=limit,
            result_set_size=result_set_size,
            results=tuple(raw_results),
        )

    def fetch_all(
        self,
        *,
        domain: str,
        page_size: int = DEFAULT_PAGE_SIZE,
        query: str = "",
        maximum_pages: int = 1000,
    ) -> tuple[dict[str, Any], ...]:
        """Retrieve every catalog result for one domain and query."""

        if page_size < 1:
            raise ValueError(
                "page_size must be greater than zero."
            )

        if maximum_pages < 1:
            raise ValueError(
                "maximum_pages must be greater than zero."
            )

        results: list[dict[str, Any]] = []
        offset = 0

        for _page_number in range(1, maximum_pages + 1):
            page = self.fetch_page(
                domain=domain,
                offset=offset,
                limit=page_size,
                query=query,
            )

            results.extend(page.results)

            if len(results) >= page.result_set_size:
                return tuple(results)

            if not page.results:
                raise SocrataCatalogError(
                    "Socrata catalog pagination ended before the "
                    "reported resultSetSize was reached."
                )

            offset += len(page.results)

        raise SocrataCatalogError(
            "Socrata catalog pagination exceeded the configured "
            f"maximum of {maximum_pages} pages."
        )

    def _request(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform one Discovery API request and decode its JSON object."""

        try:
            response = requests.get(
                SOCRATA_CATALOG_URL,
                params=params,
                headers={
                    "Accept": "application/json",
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SocrataCatalogError(
                f"Socrata catalog request failed: {exc}"
            ) from exc

        try:
            payload = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise SocrataCatalogError(
                "Socrata catalog returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise SocrataCatalogError(
                "Socrata catalog response must contain a "
                "top-level object."
            )

        return payload

    @staticmethod
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
# ======================================================================
# END: SOCRATA_CATALOG_CLIENT
# ======================================================================