# ======================================================================
# FILE: aurora/subsystems/wu_chat/tests/test_workspace_context.py
# START: WU_WORKSPACE_CONTEXT_TESTS
# ======================================================================

from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, override_settings

from aurora.subsystems.wu_chat.services.workspace_context import (
    WorkspaceContextError,
    resolve_repository_request,
)


class RepositoryRequestResolutionTests(
    SimpleTestCase
):
    """Protect bounded Wu repository continuation resolution."""

    def test_resolves_one_repository_request(self):
        with TemporaryDirectory() as temporary_root:
            repository_root = Path(
                temporary_root
            )

            target = (
                repository_root
                / "aurora"
                / "example.md"
            )

            target.parent.mkdir(
                parents=True
            )

            target.write_text(
                "repository authority\n",
                encoding="utf-8",
            )

            with override_settings(
                BASE_DIR=repository_root
            ):
                result = resolve_repository_request(
                    "[REQUEST_FILE: aurora/example.md]"
                )

            self.assertIsNotNone(
                result
            )

            self.assertEqual(
                result.file_path,
                "aurora/example.md",
            )

            self.assertEqual(
                result.original_content,
                "repository authority\n",
            )

    def test_returns_none_without_repository_request(self):
        result = resolve_repository_request(
            "No additional repository authority is required."
        )

        self.assertIsNone(
            result
        )

    def test_rejects_repository_escape(self):
        with TemporaryDirectory() as temporary_root:
            repository_root = Path(
                temporary_root
            )

            with override_settings(
                BASE_DIR=repository_root
            ):
                with self.assertRaisesRegex(
                    WorkspaceContextError,
                    "escapes the repository root",
                ):
                    resolve_repository_request(
                        "[REQUEST_FILE: ../outside.md]"
                    )

    def test_rejects_absolute_path(self):
        with TemporaryDirectory() as temporary_root:
            repository_root = Path(
                temporary_root
            )

            with override_settings(
                BASE_DIR=repository_root
            ):
                with self.assertRaisesRegex(
                    WorkspaceContextError,
                    "Absolute file paths are not permitted",
                ):
                    resolve_repository_request(
                        "[REQUEST_FILE: /etc/passwd]"
                    )

    def test_rejects_multiple_repository_requests(self):
        with self.assertRaisesRegex(
            WorkspaceContextError,
            "multiple repository files",
        ):
            resolve_repository_request(
                "[REQUEST_FILE: aurora/one.md]\n"
                "[REQUEST_FILE: aurora/two.md]"
            )


# ======================================================================
# END: WU_WORKSPACE_CONTEXT_TESTS
# ======================================================================