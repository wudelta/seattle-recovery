# ======================================================================
# FILE: aurora/management/commands/backup_to_usb.py
# START: USB_RECOVERY_BACKUP_COMMAND
# ======================================================================

import json
import os
import shutil
import tempfile

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import docker

from django.core.management.base import (
    BaseCommand,
    CommandError,
)


RECOVERY_MEDIA_ROOT = Path("/recovery_media")
RECOVERY_DIRECTORY_NAME = "aurora_recovery"
RECOVERY_MANIFEST_NAME = "RECOVERY_MANIFEST"
RECOVERY_FORMAT_VERSION = 1

ENV_SOURCE = Path("/app/.env")

SAFETY_MARGIN_MIN_BYTES = 16 * 1024 * 1024
SAFETY_MARGIN_PERCENT = 0.10

DISPLAY_CONTENT_LIMIT = 20


class Command(BaseCommand):
    """
    Create or refresh the Aurora catastrophic-recovery USB baseline.

    Aurora owns only the aurora_recovery directory on selected media.
    Files outside that directory are never modified.
    """

    help = (
        "Create or refresh an Aurora USB recovery set containing one fresh "
        "PostgreSQL dump and the repository .env file."
    )

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        self._validate_runtime()

        dump_path = None

        try:
            self.stdout.write(
                "Creating fresh PostgreSQL recovery dump..."
            )

            dump_path = self._create_database_dump()

            required_bytes = self._calculate_required_space(
                dump_path
            )

            media = self._discover_media()

            selected = self._select_media(
                media,
                required_bytes,
            )

            self._process_selected_media(
                selected,
                dump_path,
                required_bytes,
            )

        finally:
            if dump_path is not None:
                try:
                    dump_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def _validate_runtime(self) -> None:
        if not RECOVERY_MEDIA_ROOT.exists():
            raise CommandError(
                f'Recovery-media root "{RECOVERY_MEDIA_ROOT}" does not exist.'
            )

        if not RECOVERY_MEDIA_ROOT.is_dir():
            raise CommandError(
                f'Recovery-media root "{RECOVERY_MEDIA_ROOT}" is not a directory.'
            )

        if not ENV_SOURCE.exists():
            raise CommandError(
                f'Required recovery file "{ENV_SOURCE}" does not exist.'
            )

        if not ENV_SOURCE.is_file():
            raise CommandError(
                f'Required recovery file "{ENV_SOURCE}" is not a file.'
            )

    def _create_database_dump(self) -> Path:
        database_name = (
            os.environ.get("DB_NAME", "").strip()
            or "hopehub_aurora"
        )

        database_user = (
            os.environ.get("DB_USER", "").strip()
            or "postgres"
        )

        docker_client = None

        temporary_path = None

        try:
            docker_client = docker.from_env()

            postgres = docker_client.containers.get(
                "seattle_postgres"
            )

            temp_file = tempfile.NamedTemporaryFile(
                prefix="aurora_usb_recovery_",
                suffix=".sql",
                dir="/app",
                delete=False,
            )

            temporary_path = Path(
                temp_file.name
            )

            temp_file.close()

            exec_result = docker_client.api.exec_create(
                postgres.id,
                [
                    "pg_dump",
                    "-U",
                    database_user,
                    "-d",
                    database_name,
                ],
                stdout=True,
                stderr=True,
            )

            exec_id = exec_result["Id"]

            stream = docker_client.api.exec_start(
                exec_id,
                stream=True,
                demux=True,
            )

            stderr_chunks = []

            with temporary_path.open("wb") as output:
                for stdout_chunk, stderr_chunk in stream:
                    if stdout_chunk:
                        output.write(
                            stdout_chunk
                        )

                    if stderr_chunk:
                        stderr_chunks.append(
                            stderr_chunk
                        )

            inspection = docker_client.api.exec_inspect(
                exec_id
            )

            exit_code = inspection.get(
                "ExitCode"
            )

            if exit_code != 0:
                stderr = b"".join(
                    stderr_chunks
                ).decode(
                    "utf-8",
                    errors="replace",
                ).strip()

                raise CommandError(
                    "PostgreSQL backup failed"
                    + (
                        f": {stderr}"
                        if stderr
                        else "."
                    )
                )

            if (
                not temporary_path.exists()
                or temporary_path.stat().st_size == 0
            ):
                raise CommandError(
                    "PostgreSQL backup produced an empty dump."
                )

            return temporary_path

        except docker.errors.DockerException as exc:
            if temporary_path is not None:
                temporary_path.unlink(
                    missing_ok=True
                )

            raise CommandError(
                f"Unable to create PostgreSQL backup through Docker: {exc}"
            ) from exc

        except OSError as exc:
            if temporary_path is not None:
                temporary_path.unlink(
                    missing_ok=True
                )

            raise CommandError(
                f"Unable to write temporary PostgreSQL backup: {exc}"
            ) from exc

        finally:
            if docker_client is not None:
                docker_client.close()

    def _calculate_required_space(
        self,
        dump_path: Path,
    ) -> int:
        dump_bytes = dump_path.stat().st_size
        env_bytes = ENV_SOURCE.stat().st_size

        payload_bytes = (
            dump_bytes
            + env_bytes
            + 4096
        )

        safety_margin = max(
            int(
                payload_bytes
                * SAFETY_MARGIN_PERCENT
            ),
            SAFETY_MARGIN_MIN_BYTES,
        )

        required_bytes = (
            payload_bytes
            + safety_margin
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            "RECOVERY PAYLOAD"
        )

        self.stdout.write(
            f"  DATABASE DUMP: {self._format_bytes(dump_bytes)}"
        )

        self.stdout.write(
            f"  .ENV:          {self._format_bytes(env_bytes)}"
        )

        self.stdout.write(
            f"  SPACE REQUIRED:{self._format_bytes(required_bytes):>11}"
        )

        return required_bytes

    def _discover_media(
        self,
    ) -> list[Path]:
        candidates = []

        for path in sorted(
            RECOVERY_MEDIA_ROOT.iterdir(),
            key=lambda item: item.name.lower(),
        ):
            try:
                if (
                    path.is_dir()
                    and path.is_mount()
                ):
                    candidates.append(
                        path
                    )
            except OSError:
                continue

        if not candidates:
            raise CommandError(
                "No mounted recovery media was found under "
                f'"{RECOVERY_MEDIA_ROOT}".'
            )

        return candidates

    def _select_media(
        self,
        media: list[Path],
        required_bytes: int,
    ) -> Path:
        self.stdout.write(
            ""
        )

        self.stdout.write(
            "DETECTED REMOVABLE MEDIA"
        )

        for index, path in enumerate(
            media,
            start=1,
        ):
            self._display_media(
                index,
                path,
                required_bytes,
            )

        if len(media) == 1:
            selected = media[0]

            answer = input(
                f'\nUse "{selected.name}"? [y/N]: '
            ).strip().lower()

            if answer not in {
                "y",
                "yes",
            }:
                raise CommandError(
                    "USB recovery cancelled."
                )

            return selected

        while True:
            answer = input(
                "\nSelect media number or C to cancel: "
            ).strip()

            if answer.lower() == "c":
                raise CommandError(
                    "USB recovery cancelled."
                )

            try:
                selected_index = int(
                    answer
                )
            except ValueError:
                self.stdout.write(
                    "Enter a listed media number or C."
                )

                continue

            if (
                selected_index < 1
                or selected_index > len(media)
            ):
                self.stdout.write(
                    "Select one of the listed media numbers."
                )

                continue

            return media[
                selected_index - 1
            ]

    def _display_media(
        self,
        index: int,
        path: Path,
        required_bytes: int,
    ) -> None:
        usage = shutil.disk_usage(
            path
        )

        recovery_directory = (
            path
            / RECOVERY_DIRECTORY_NAME
        )

        recovery_bytes = (
            self._directory_size(
                recovery_directory
            )
            if recovery_directory.exists()
            else 0
        )

        effective_free = (
            usage.free
            + recovery_bytes
        )

        recognized = (
            self._is_recognized_recovery_media(
                path
            )
        )

        filesystem = self._filesystem_type(
            path
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            f"{index}. {path.name}"
        )

        self.stdout.write(
            f"   PATH:            {path}"
        )

        self.stdout.write(
            f"   FILESYSTEM:      {filesystem}"
        )

        self.stdout.write(
            f"   TOTAL SPACE:     {self._format_bytes(usage.total)}"
        )

        self.stdout.write(
            f"   SPACE USED:      {self._format_bytes(usage.used)}"
        )

        self.stdout.write(
            f"   SPACE FREE:      {self._format_bytes(usage.free)}"
        )

        self.stdout.write(
            f"   SPACE REQUIRED:  {self._format_bytes(required_bytes)}"
        )

        if recovery_bytes:
            self.stdout.write(
                "   REPLACEABLE USB: "
                f"{self._format_bytes(recovery_bytes)}"
            )

            self.stdout.write(
                "   EFFECTIVE FREE:  "
                f"{self._format_bytes(effective_free)}"
            )

        self.stdout.write(
            "   AURORA RECOVERY: "
            + (
                "RECOGNIZED"
                if recognized
                else "NOT INITIALIZED"
            )
        )

        self.stdout.write(
            "   CONTENTS:"
        )

        children = list(
            sorted(
                path.iterdir(),
                key=lambda item: item.name.lower(),
            )
        )

        if not children:
            self.stdout.write(
                "     <empty>"
            )
        else:
            for child in children[
                :DISPLAY_CONTENT_LIMIT
            ]:
                suffix = (
                    "/"
                    if child.is_dir()
                    else ""
                )

                self.stdout.write(
                    f"     {child.name}{suffix}"
                )

            if len(children) > DISPLAY_CONTENT_LIMIT:
                self.stdout.write(
                    "     ..."
                )

    def _process_selected_media(
        self,
        media: Path,
        dump_path: Path,
        required_bytes: int,
    ) -> None:
        self.stdout.write(
            ""
        )

        self.stdout.write(
            f'SELECTED MEDIA: "{media.name}"'
        )

        usage = shutil.disk_usage(
            media
        )

        recovery_directory = (
            media
            / RECOVERY_DIRECTORY_NAME
        )

        recognized = (
            self._is_recognized_recovery_media(
                media
            )
        )

        recovery_bytes = (
            self._directory_size(
                recovery_directory
            )
            if recovery_directory.exists()
            else 0
        )

        effective_free = (
            usage.free
            + recovery_bytes
        )

        if recognized:
            if effective_free < required_bytes:
                raise CommandError(
                    "The existing Aurora recovery media does not have "
                    "enough effective free space for the new recovery set."
                )

            self._confirm_refresh(
                media
            )

            self._write_recovery_set(
                media,
                dump_path,
            )

            return

        if recovery_directory.exists():
            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.WARNING(
                    f'A directory named "{RECOVERY_DIRECTORY_NAME}" already '
                    "exists, but it does not contain a valid Aurora recovery "
                    "manifest."
                )
            )

            self._handle_unrecognized_media(
                media,
                dump_path,
                required_bytes,
                allow_add=False,
            )

            return

        self._handle_unrecognized_media(
            media,
            dump_path,
            required_bytes,
            allow_add=(
                usage.free
                >= required_bytes
            ),
        )

    def _handle_unrecognized_media(
        self,
        media: Path,
        dump_path: Path,
        required_bytes: int,
        *,
        allow_add: bool,
    ) -> None:
        usage = shutil.disk_usage(
            media
        )

        if usage.total < required_bytes:
            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.ERROR(
                    "This device is too small to hold the Aurora "
                    "recovery set even if reformatted."
                )
            )

            raise CommandError(
                "Use different USB media."
            )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            self.style.WARNING(
                "This is not recognized Aurora recovery media."
            )
        )

        choices = []

        if allow_add:
            choices.append(
                (
                    "A",
                    "Add Aurora recovery area without deleting existing files",
                )
            )

        choices.append(
            (
                "F",
                "Format and wipe media, then initialize Aurora recovery",
            )
        )

        choices.append(
            (
                "C",
                "Cancel and use different media",
            )
        )

        self.stdout.write(
            ""
        )

        for key, description in choices:
            self.stdout.write(
                f"  {key}. {description}"
            )

        allowed = {
            key
            for key, _description in choices
        }

        while True:
            answer = input(
                "\nChoose an option: "
            ).strip().upper()

            if answer not in allowed:
                self.stdout.write(
                    "Choose one of the listed options."
                )

                continue

            if answer == "C":
                raise CommandError(
                    "USB recovery cancelled."
                )

            if answer == "A":
                self._confirm_add(
                    media
                )

                self._write_recovery_set(
                    media,
                    dump_path,
                )

                return

            if answer == "F":
                self._format_not_available(
                    media
                )

    def _confirm_refresh(
        self,
        media: Path,
    ) -> None:
        answer = input(
            "\nRefresh the existing Aurora recovery area on "
            f'"{media.name}"? [y/N]: '
        ).strip().lower()

        if answer not in {
            "y",
            "yes",
        }:
            raise CommandError(
                "USB recovery cancelled."
            )

    def _confirm_add(
        self,
        media: Path,
    ) -> None:
        self.stdout.write(
            ""
        )

        self.stdout.write(
            "Aurora will create:"
        )

        self.stdout.write(
            f"  {media / RECOVERY_DIRECTORY_NAME}"
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            "Files outside that directory will not be modified."
        )

        answer = input(
            "Continue? [y/N]: "
        ).strip().lower()

        if answer not in {
            "y",
            "yes",
        }:
            raise CommandError(
                "USB recovery cancelled."
            )

    def _format_not_available(
        self,
        media: Path,
    ) -> None:
        self.stdout.write(
            ""
        )

        self.stdout.write(
            self.style.WARNING(
                "FORMAT REQUESTED"
            )
        )

        self.stdout.write(
            f"  TARGET: {media}"
        )

        self.stdout.write(
            f"  CURRENT FILESYSTEM: {self._filesystem_type(media)}"
        )

        self.stdout.write(
            "  INTENDED LABEL: RECOVERY_MEDIA"
        )

        self.stdout.write(
            ""
        )

        raise CommandError(
            "Formatting requires a host-side block-device authority. "
            "The Django container will not be granted raw disk access. "
            "No files were modified."
        )

    def _write_recovery_set(
        self,
        media: Path,
        dump_path: Path,
    ) -> None:
        recovery_directory = (
            media
            / RECOVERY_DIRECTORY_NAME
        )

        staging_directory = (
            media
            / ".aurora_recovery_staging"
        )

        previous_directory = (
            media
            / ".aurora_recovery_previous"
        )

        if staging_directory.exists():
            shutil.rmtree(
                staging_directory
            )

        if previous_directory.exists():
            shutil.rmtree(
                previous_directory
            )

        try:
            staging_directory.mkdir()

            env_destination = (
                staging_directory
                / ".env"
            )

            dump_destination = (
                staging_directory
                / "hopehub_aurora.sql"
            )

            shutil.copy2(
                ENV_SOURCE,
                env_destination,
            )

            shutil.copy2(
                dump_path,
                dump_destination,
            )

            manifest = {
                "format_version": RECOVERY_FORMAT_VERSION,
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "contents": [
                    ".env",
                    "hopehub_aurora.sql",
                ],
                "database": {
                    "name": (
                        os.environ.get(
                            "DB_NAME",
                            "",
                        ).strip()
                        or "hopehub_aurora"
                    ),
                    "dump_file": "hopehub_aurora.sql",
                },
                "security": {
                    "application_encryption": False,
                    "control": (
                        "Physical separation and physical custody of "
                        "recovery media."
                    ),
                },
            }

            manifest_path = (
                staging_directory
                / RECOVERY_MANIFEST_NAME
            )

            manifest_path.write_text(
                json.dumps(
                    manifest,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            self._validate_staging(
                staging_directory
            )

            if recovery_directory.exists():
                recovery_directory.rename(
                    previous_directory
                )

            staging_directory.rename(
                recovery_directory
            )

            if previous_directory.exists():
                shutil.rmtree(
                    previous_directory
                )

        except (
            OSError,
            shutil.Error,
        ) as exc:
            if staging_directory.exists():
                shutil.rmtree(
                    staging_directory,
                    ignore_errors=True,
                )

            if (
                previous_directory.exists()
                and not recovery_directory.exists()
            ):
                previous_directory.rename(
                    recovery_directory
                )

            raise CommandError(
                f"Unable to write Aurora recovery set: {exc}"
            ) from exc

        self.stdout.write(
            ""
        )

        self.stdout.write(
            self.style.SUCCESS(
                "BACKUP COMPLETE"
            )
        )

        self.stdout.write(
            f"MEDIA: {media.name}"
        )

        self.stdout.write(
            f"RECOVERY DIRECTORY: {recovery_directory}"
        )

        self.stdout.write(
            "CONTENTS:"
        )

        self.stdout.write(
            "  RECOVERY_MANIFEST"
        )

        self.stdout.write(
            "  .env"
        )

        self.stdout.write(
            "  hopehub_aurora.sql"
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            "Files outside aurora_recovery/ were not modified."
        )

    def _validate_staging(
        self,
        staging_directory: Path,
    ) -> None:
        expected = {
            RECOVERY_MANIFEST_NAME,
            ".env",
            "hopehub_aurora.sql",
        }

        actual = {
            path.name
            for path in staging_directory.iterdir()
        }

        if actual != expected:
            raise CommandError(
                "Recovery staging validation failed: unexpected contents."
            )

        env_path = (
            staging_directory
            / ".env"
        )

        dump_path = (
            staging_directory
            / "hopehub_aurora.sql"
        )

        manifest_path = (
            staging_directory
            / RECOVERY_MANIFEST_NAME
        )

        if env_path.stat().st_size == 0:
            raise CommandError(
                "Recovery staging validation failed: .env is empty."
            )

        if dump_path.stat().st_size == 0:
            raise CommandError(
                "Recovery staging validation failed: database dump is empty."
            )

        try:
            manifest = json.loads(
                manifest_path.read_text(
                    encoding="utf-8"
                )
            )
        except (
            OSError,
            json.JSONDecodeError,
        ) as exc:
            raise CommandError(
                "Recovery staging validation failed: manifest is invalid."
            ) from exc

        if (
            manifest.get("format_version")
            != RECOVERY_FORMAT_VERSION
        ):
            raise CommandError(
                "Recovery staging validation failed: unsupported manifest "
                "version."
            )

    def _is_recognized_recovery_media(
        self,
        media: Path,
    ) -> bool:
        manifest_path = (
            media
            / RECOVERY_DIRECTORY_NAME
            / RECOVERY_MANIFEST_NAME
        )

        if not manifest_path.is_file():
            return False

        try:
            manifest = json.loads(
                manifest_path.read_text(
                    encoding="utf-8"
                )
            )
        except (
            OSError,
            json.JSONDecodeError,
        ):
            return False

        return (
            manifest.get("format_version")
            == RECOVERY_FORMAT_VERSION
        )

    def _directory_size(
        self,
        path: Path,
    ) -> int:
        if not path.exists():
            return 0

        total = 0

        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total += (
                        item.stat().st_size
                    )
        except OSError:
            return 0

        return total

    def _filesystem_type(
        self,
        path: Path,
    ) -> str:
        try:
            mounts = Path(
                "/proc/self/mounts"
            ).read_text(
                encoding="utf-8"
            )
        except OSError:
            return "UNKNOWN"

        resolved = str(
            path.resolve()
        )

        best_match = None
        best_fstype = None

        for line in mounts.splitlines():
            fields = line.split()

            if len(fields) < 3:
                continue

            mount_point = (
                fields[1]
                .replace("\\040", " ")
            )

            fstype = fields[2]

            if (
                resolved == mount_point
                or resolved.startswith(
                    mount_point.rstrip("/")
                    + "/"
                )
            ):
                if (
                    best_match is None
                    or len(mount_point) > len(best_match)
                ):
                    best_match = mount_point
                    best_fstype = fstype

        return (
            best_fstype
            or "UNKNOWN"
        )

    def _format_bytes(
        self,
        value: int,
    ) -> str:
        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB",
        ]

        size = float(
            value
        )

        for unit in units:
            if (
                size < 1024
                or unit == units[-1]
            ):
                if unit == "B":
                    return f"{int(size)} {unit}"

                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{value} B"


# ======================================================================
# END: USB_RECOVERY_BACKUP_COMMAND
# ======================================================================