# FILE: aurora/sync_autospec.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:45.558858+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/management/commands/sync_autospec.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: handle, strip_existing_spec

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[sync_autospec.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
import os
import re
from django.core.management.base import BaseCommand
from django.utils import timezone
from aurora.minion_array.generate_python import inject_autospec_and_write

class Command(BaseCommand):
    help = "Strictly targets and updates Auto-Spec headers inside local project directories."

    def handle(self, *args, **options):
        # HARD BOUNDARY: Only scan your direct functional workspace directories
        target_project_dirs = ['aurora', 'hopehub']
        target_extensions = ['.py', '.js', '.ts', '.html', '.css']
        project_root = os.getcwd()
        processed_count = 0

        self.stdout.write(self.style.WARNING("Starting isolated local project crawl..."))

        for target_dir in target_project_dirs:
            target_path = os.path.join(project_root, target_dir)
            if not os.path.exists(target_path):
                continue

            for root, dirs, files in os.walk(target_path):
                # Hard skip migration histories and cache directories
                dirs[:] = [d for d in dirs if d not in {'migrations', '__pycache__', '.pytest_cache'}]

                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in target_extensions:
                        continue

                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, project_root)

                    self.stdout.write(f"Documenting Project Asset: {relative_path}")

                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            raw_code = f.read()

                        clean_code = self.strip_existing_spec(raw_code, relative_path)

                        placeholder_diagram = (
                            f"graph TD\n"
                            f"    A[{file}] --> B(System Kernel)\n"
                            f"    B --> C{{Ecosystem Check}}\n"
                            f"    C -->|Project Bind| D[{target_dir.upper()}]"
                        )

                        final_code = inject_autospec_and_write(
                            file_path=relative_path,
                            project_name=target_dir,
                            generated_code=clean_code,
                            architectural_flow_diagram=placeholder_diagram
                        )

                        tmp_path = f"{full_path}.tmp"
                        with open(tmp_path, 'w', encoding='utf-8') as f:
                            f.write(final_code)

                        os.replace(tmp_path, full_path)
                        processed_count += 1

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed processing {relative_path}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Finished. Documented {processed_count} native workspace assets."))

    def strip_existing_spec(self, content, path):
        """Prevents header duplication by scrubbing existing automated spec patterns."""
        # FIXED HERE: Added [1] to safely extract extension from tuple
        extension = os.path.splitext(path)[1].lower()
        
        if extension == '.py':
            content = re.sub(r'^# FILE:.*?\n', '', content)
            return re.sub(r'^"""\s*AUTO-SPEC DOCUMENTATION.*?"""\n', '', content, flags=re.DOTALL).strip()
        elif extension in ['.js', '.ts', '.css']:
            content = re.sub(r'^// FILE:.*?\n', '', content)
            return re.sub(r'^/\*\s*AUTO-SPEC DOCUMENTATION.*?\*/\n', '', content, flags=re.DOTALL).strip()
        elif extension == '.html':
            return re.sub(r'^<!-- FILE:.*? -->\n<!--\s*AUTO-SPEC DOCUMENTATION.*?-->\n', '', content, flags=re.DOTALL).strip()
        return content.strip()