# ======================================================================
# FILE: hopehub/subsystems/resource_sources/king_county_211/dataset_registry.py
# START: KING_COUNTY_211_DATASET_REGISTRY
# ======================================================================
"""Canonical registry of candidate King County resource datasets."""

from dataclasses import dataclass
from enum import StrEnum


KING_COUNTY_DATA_DOMAIN = "data.kingcounty.gov"
KING_COUNTY_DATA_BASE_URL = f"https://{KING_COUNTY_DATA_DOMAIN}"
KING_COUNTY_CATALOG_URL = (
    "https://api.us.socrata.com/api/catalog/v1"
    f"?domains={KING_COUNTY_DATA_DOMAIN}&only=datasets"
)
KING_COUNTY_APP_TOKEN_ENV_VAR = "KING_COUNTY_211_APP_TOKEN"


class DatasetVerificationStatus(StrEnum):
    """Verification state for a candidate resource dataset."""

    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    DUPLICATE = "DUPLICATE"
    DEPRECATED = "DEPRECATED"


@dataclass(frozen=True)
class KingCountyDataset:
    """One candidate King County dataset and its verification evidence."""

    key: str
    dataset_id: str
    expected_name: str
    expected_purpose: str
    verification_status: DatasetVerificationStatus
    verification_notes: str

    @property
    def metadata_url(self) -> str:
        """Return the public Socrata metadata URL for this dataset."""

        return (
            f"{KING_COUNTY_DATA_BASE_URL}/api/views/"
            f"{self.dataset_id}"
        )

    @property
    def query_url(self) -> str:
        """Return the Socrata version-three query endpoint."""

        return (
            f"{KING_COUNTY_DATA_BASE_URL}/api/v3/views/"
            f"{self.dataset_id}/query.json"
        )

    @property
    def acquisition_enabled(self) -> bool:
        """Return whether this dataset is approved for acquisition."""

        return (
            self.verification_status
            == DatasetVerificationStatus.VERIFIED
        )


DATASETS = (
    KingCountyDataset(
        key="human_services",
        dataset_id="x6fc-6pka",
        expected_name="General Human Services Providers and Basic Needs",
        expected_purpose=(
            "Candidate source for food assistance, cash support, clothing, "
            "hygiene facilities, and other basic-needs services."
        ),
        verification_status=DatasetVerificationStatus.REJECTED,
        verification_notes=(
            "The King County metadata endpoint returned HTTP 404. "
            "No active dataset exists under this identifier."
        ),
    ),
    KingCountyDataset(
        key="shelters",
        dataset_id="g673-8gsh",
        expected_name="Affordable Housing and Emergency Overnight Shelters",
        expected_purpose=(
            "Candidate source for shelters, temporary housing assistance, "
            "and emergency placement services."
        ),
        verification_status=DatasetVerificationStatus.REJECTED,
        verification_notes=(
            "The King County metadata endpoint returned HTTP 404. "
            "No active dataset exists under this identifier."
        ),
    ),
    KingCountyDataset(
        key="health_clinics",
        dataset_id="vgh2-9egh",
        expected_name="Public Health Centers and Community Clinics",
        expected_purpose=(
            "Candidate source for public medical providers, community "
            "clinics, and mobile dental services."
        ),
        verification_status=DatasetVerificationStatus.REJECTED,
        verification_notes=(
            "The King County metadata endpoint returned HTTP 404. "
            "No active dataset exists under this identifier."
        ),
    ),
    KingCountyDataset(
        key="rent_assistance",
        dataset_id="6473-b8y5",
        expected_name="Eviction Prevention and Emergency Rent Assistance",
        expected_purpose=(
            "Candidate source for rental assistance, displacement "
            "prevention, and related legal-aid services."
        ),
        verification_status=DatasetVerificationStatus.REJECTED,
        verification_notes=(
            "The King County metadata endpoint returned HTTP 404. "
            "No active dataset exists under this identifier."
        ),
    ),
    KingCountyDataset(
        key="behavioral_health",
        dataset_id="sep3-3pj3",
        expected_name=(
            "Mental Health and Substance Use Disorder Providers Directory"
        ),
        expected_purpose=(
            "Candidate source for behavioral-health and substance-use-"
            "disorder provider records."
        ),
        verification_status=DatasetVerificationStatus.VERIFIED,
        verification_notes=(
            "The active dataset is titled 'King County Mental Health and "
            "Substance Use-Disorder Providers.' It contains 23 columns and "
            "is attributed to the King County Behavioral Health and "
            "Recovery Division. Its description identifies it as the "
            "directory of contracted mental-health and substance-use "
            "providers."
        ),
    ),
    KingCountyDataset(
        key="specialized_health",
        dataset_id="nqri-czhj",
        expected_name="Specialized Vulnerable Population Care Sites",
        expected_purpose=(
            "Candidate source for specialized health interventions and "
            "care sites serving vulnerable populations."
        ),
        verification_status=DatasetVerificationStatus.REJECTED,
        verification_notes=(
            "The active view is titled 'Homelessness and COVID-19.' "
            "It reports pandemic impacts among people experiencing "
            "homelessness and is not a current service-provider directory."
        ),
    ),
    KingCountyDataset(
        key="community_events",
        dataset_id="mnxa-8m4g",
        expected_name="Community and Human Services Calendar",
        expected_purpose=(
            "Candidate source for outreach events, mobile distribution, "
            "and localized service pop-ups."
        ),
        verification_status=DatasetVerificationStatus.REJECTED,
        verification_notes=(
            "The active view is a King County master calendar categorized "
            "under County Operations. It is not a resource-provider "
            "dataset."
        ),
    ),
    KingCountyDataset(
        key="youth_family_resources",
        dataset_id="2be9-wu5b",
        expected_name="Best Starts for Kids Funding Award Database",
        expected_purpose=(
            "Candidate source for funded youth, family-resource, and early-"
            "intervention organizations."
        ),
        verification_status=DatasetVerificationStatus.REJECTED,
        verification_notes=(
            "The dataset contains funding focus, strategy, partner, "
            "project description, contract amount, and council district. "
            "It does not provide the current service locations, contact "
            "information, eligibility, or operating details required by "
            "the Resource Finder."
        ),
    ),
    KingCountyDataset(
        key="service_transportation",
        dataset_id="64yn-5kas",
        expected_name="King County Metro Solid Ground Circulator",
        expected_purpose=(
            "Candidate source for transportation routes connecting people "
            "to social-service locations."
        ),
        verification_status=DatasetVerificationStatus.REJECTED,
        verification_notes=(
            "The dataset contains route geometry and numeric identifiers. "
            "It does not contain resource-provider or service-location "
            "records suitable for the Resource Finder."
        ),
    ),
)


DATASETS_BY_KEY = {
    dataset.key: dataset
    for dataset in DATASETS
}

DATASETS_BY_ID = {
    dataset.dataset_id: dataset
    for dataset in DATASETS
}

VERIFIED_DATASETS = tuple(
    dataset
    for dataset in DATASETS
    if dataset.acquisition_enabled
)


def get_dataset_by_key(key: str) -> KingCountyDataset:
    """Return one registered dataset by its repository-owned key."""

    try:
        return DATASETS_BY_KEY[key]
    except KeyError as exc:
        raise KeyError(
            f'Unknown King County dataset key: "{key}".'
        ) from exc


def get_dataset_by_id(dataset_id: str) -> KingCountyDataset:
    """Return one registered dataset by its Socrata identifier."""

    try:
        return DATASETS_BY_ID[dataset_id]
    except KeyError as exc:
        raise KeyError(
            f'Unknown King County dataset ID: "{dataset_id}".'
        ) from exc
# ======================================================================
# END: KING_COUNTY_211_DATASET_REGISTRY
# ======================================================================