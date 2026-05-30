# filepath: aurora/management/commands/ai_sync.py
"""Aurora Forge Automated AI Reseed & Constraint Sync Engine."""

import json
from django.core.management.base import BaseCommand
from hopehub.models import TechnicalConstraint, GovernanceSection


# Ensure class name is exactly "Command" (Case-Sensitive)
class Command(BaseCommand):
    help = "Automates AI context reseed extraction and saves updated compliance constraints."

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-rule', 
            type=str, 
            help="Update a constraint by key. Format: rule_key:dict_key:value"
        )

    def handle(self, *args, **options):
        # Handle Inline Update Workflow if requested
        if options['update_rule']:
            self._execute_inline_update(options['update_rule'])
            return

        # Handle AI Reseed Extraction Workflow (Prints everything for the AI)
        self.stdout.write("\n" + "="*70)
        self.stdout.write("🚀 COPY EVERY LINE BELOW THIS TO RESEED YOUR AI CONTEXT WINDOW")
        self.stdout.write("="*70 + "\n")

        self.stdout.write("PROMPT CONTEXT MASTER GUIDELINE:")
        self.stdout.write("You are an adaptive AI collaborator engineering HopeHub and Aurora.")
        self.stdout.write("You must strictly adhere to the project constraints and compliance rules detailed below.\n")

        # 1. Pull Human-Readable Regulatory Mandates
        self.stdout.write("=== SECTION 1: GOVERNANCE AND COMPLIANCE MANDATES ===")
        for gs in GovernanceSection.objects.all():
            self.stdout.write(f"\n[POLICY: {gs.title}]")
            self.stdout.write(gs.body_text)

        # 2. Pull Machine-Readable AI Constraints (HopeHub + Aurora)
        self.stdout.write("\n=== SECTION 2: SYSTEM ARCHITECTURAL CONSTRAINTS ===")
        for tc in TechnicalConstraint.objects.filter(is_active=True):
            self.stdout.write(f"\nConstraint Key: {tc.rule_key}")
            self.stdout.write(f"Description: {tc.description}")
            self.stdout.write(json.dumps(tc.constraint_data, indent=2))

        self.stdout.write("\n" + "="*70)
        self.stdout.write("✅ END OF RESEED MATRIX // WORKSPACE READY")
        self.stdout.write("="*70 + "\n")

    def _execute_inline_update(self, update_string):
        """Safely updates a target nested dictionary rule key inside the database."""
        try:
            rule_key, dict_key, value = update_string.split(':')
            tc = TechnicalConstraint.objects.get(rule_key=rule_key)
            
            # Simple type parsing for arrays or booleans
            if value.startswith('[') and value.endswith(']'):
                parsed_value = [v.strip().strip("'\"") for v in value[1:-1].split(',')]
            elif value.lower() == 'true':
                parsed_value = True
            elif value.lower() == 'false':
                parsed_value = False
            else:
                parsed_value = value

            tc.constraint_data[dict_key] = parsed_value
            tc.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated database constraint record '{rule_key}' -> {dict_key} = {parsed_value}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to parse or update constraint matrix: {str(e)}"))
