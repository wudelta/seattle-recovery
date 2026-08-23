# ======================================================================
# FILE: aurora/subsystems/hansel/services/validation.py
# START: HANSEL_REPOSITORY_VALIDATION_SERVICE
# ======================================================================

from dataclasses import dataclass
from pathlib import Path

from aurora.subsystems.hansel.validators.hansel_contract import (
    HanselContractValidation,
    validate_hansel_contract,
)


@dataclass(frozen=True)
class HanselRepositoryValidation:
    """Deterministic validation result for all recognized subsystems."""

    results: tuple[HanselContractValidation, ...]

    @property
    def is_valid(self) -> bool:
        return all(
            result.is_valid
            for result in self.results
        )

    @property
    def valid_count(self) -> int:
        return sum(
            result.is_valid
            for result in self.results
        )

    @property
    def invalid_count(self) -> int:
        return len(self.results) - self.valid_count


def validate_hansel_repository(
    *,
    repository_root: Path | str = ".",
) -> HanselRepositoryValidation:
    """Validate every recognized subsystem with a canonical Hansel contract."""

    root = Path(
        repository_root
    ).resolve()

    subsystems_root = (
        root
        / "aurora"
        / "subsystems"
    )

    subsystems = sorted(
        (
            path
            for path in subsystems_root.iterdir()
            if path.is_dir()
            and not path.name.startswith("__")
            and (
                path
                / "contracts"
                / "HANSEL.md"
            ).is_file()
        ),
        key=lambda path: path.name,
    )

    results = tuple(
        validate_hansel_contract(
            subsystem,
            repository_root=root,
        )
        for subsystem in subsystems
    )

    return HanselRepositoryValidation(
        results=results,
    )


# ======================================================================
# END: HANSEL_REPOSITORY_VALIDATION_SERVICE
# ======================================================================