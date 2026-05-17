# FILE: aurora/generate_docs.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:27.051131+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/management/commands/generate_docs.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: handle, strip_existing_spec

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[generate_docs.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
import os
import re
import markdown
from django.core.management.base import BaseCommand
from django.utils import timezone
from aurora.models import Document, Content
from aurora.minion_array.generate_python import inject_autospec_and_write

class Command(BaseCommand):
    help = "Consolidates crawling, database EAV population, ARCHITECTURE.md export, and print HTML compilation."

    def handle(self, *args, **options):
        target_project_dirs = ['aurora', 'hopehub']
        target_extensions = ['.py', '.js', '.ts', '.html', '.css']
        project_root = os.getcwd()
        processed_count = 0

        self.stdout.write(self.style.WARNING("⚡ Phase 1: Commencing Codebase Crawl & Database Sync..."))

        # Base array to assemble our master markdown text buffer in memory
        markdown_output = [
            "# SYSTEM ARCHITECTURE BLUEPRINT\n",
            f"**Generated:** {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            "**Ecosystem Scope:** Aurora Engine & HopeHub Layers  \n",
            "---"
        ]

        for target_dir in target_project_dirs:
            target_path = os.path.join(project_root, target_dir)
            if not os.path.exists(target_path):
                continue

            for root, dirs, files in os.walk(target_path):
                dirs[:] = [d for d in dirs if d not in {'migrations', '__pycache__', '.pytest_cache'}]

                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in target_extensions:
                        continue

                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, project_root)
                    self.stdout.write(f"Processing Matrix Asset: {relative_path}")

                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            raw_code = f.read()

                        clean_code = self.strip_existing_spec(raw_code, relative_path)

                        # Generate structured visual flowchart rules
                        placeholder_diagram = (
                            f"graph TD\n"
                            f"    A[{file}] --> B(System Kernel)\n"
                            f"    B --> C{{Ecosystem Check}}\n"
                            f"    C -->|Project Bind| D[{target_dir.upper()}]"
                        )

                        # Update code file text buffers with header comments
                        final_code = inject_autospec_and_write(
                            file_path=relative_path,
                            project_name=target_dir,
                            generated_code=clean_code,
                            architectural_flow_diagram=placeholder_diagram
                        )

                        # Save down clean header to physical storage disk
                        tmp_path = f"{full_path}.tmp"
                        with open(tmp_path, 'w', encoding='utf-8') as f:
                            f.write(final_code)
                        os.replace(tmp_path, full_path)
                        processed_count += 1

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed processing {relative_path}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"✔ Successfully synced {processed_count} files to database."))
        self.stdout.write(self.style.WARNING("⚡ Phase 2: Generating ARCHITECTURE.md & Print Layouts..."))

        # Fetch records out of database to populate the master print arrays
        documents = Document.objects.filter(title__startswith="FileSpec:").prefetch_related('content_set')
        
        for doc in documents:
            markdown_output.append(f"## {doc.title}")
            markdown_output.append(f"*Last Document Sync Pass: {doc.created_at.strftime('%Y-%m-%d')}*\n")
            
            # Fetch combined markdown block out of your content layout rows
            for item in doc.content_set.all():
                markdown_output.append(f"{item.content}\n")
            
            markdown_output.append("---\n")

        # 1. Output the master markdown file
        md_payload_string = "\n".join(markdown_output)
        md_export_path = os.path.join(project_root, 'ARCHITECTURE.md')
        with open(md_export_path, 'w', encoding='utf-8') as f:
            f.write(md_payload_string)

        # 2. Output the print-ready preview HTML page
        html_body = markdown.markdown(md_payload_string, extensions=['extra', 'fenced_code'])
        html_export_path = os.path.join(project_root, 'ARCHITECTURE_PRINT.html')
        
        print_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>System Architecture Blueprint - Print View</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #111; max-width: 800px; margin: 40px auto; padding: 0 20px; background-color: #fff; }}
        h1 {{ font-size: 2.2rem; border-bottom: 3px solid #333; padding-bottom: 10px; margin-bottom: 30px; text-align: center; }}
        h2 {{ font-size: 1.5rem; color: #2c3e50; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 40px; page-break-after: avoid; }}
        pre {{ background-color: #f6f8fa; padding: 15px; border: 1px solid #ddd; border-radius: 5px; overflow-x: auto; page-break-inside: avoid; }}
        code {{ font-family: monospace; background-color: #f6f8fa; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }}
        hr {{ border: 0; border-top: 1px solid #ccc; margin: 40px 0; }}
        @media print {{
            body {{ margin: 0; padding: 0; max-width: 100%; }}
            h2 {{ page-break-before: always; }}
            pre {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>"""

        with open(html_export_path, 'w', encoding='utf-8') as f:
            f.write(print_template)

        self.stdout.write(self.style.SUCCESS("🚀 Success! All documentation formats have been compiled and generated."))

    def strip_existing_spec(self, content, path):
        """Prevents header duplication by scrubbing existing automated spec patterns."""
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