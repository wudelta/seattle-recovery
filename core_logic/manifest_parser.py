import os
import re

class ManifestIntakeCore:
    """
    Processes the Project Aurora Functionality Manifest text blocks.
    Transforms structural criteria into compact instructions for background minions.
    """
    def __init__(self):
        self.required_keys = ["Target System", "Scenario Type", "Core Intent", "Target DB"]

    def load_manifest_from_staging(self, file_path):
        """
        Reads raw manifest string arrays directly from disk storage matrix [STAGE 1].
        """
        print(f"🔍 [MANIFEST ENGINE] Reading target brief matrix from: {file_path}")
        if not os.path.exists(file_path):
            print(f"❌ [MANIFEST CRASH] Target staging file is missing on disk.")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read().strip()
            
        if not raw_content:
            print("❌ [MANIFEST CRASH] Target text file data payload is completely blank.")
            return None
            
        return self.parse_manifest_string(raw_content)

    def parse_manifest_string(self, raw_manifest_text):
        """
        Parses ini-style feature configuration specifications cleanly.
        Extracts structural attributes into distinct dictionary keys.
        """
        parsed_data = {}
        lines = raw_manifest_text.strip().split("\n")
        
        for line in lines:
            if ":" in line and not line.startswith("["):
                key, val = line.split(":", 1)
                parsed_data[key.strip()] = val.strip()

        # Enforce validation criteria across required parameters
        missing_fields = [k for k in self.required_keys if k not in parsed_data]
        if missing_fields:
            print(f"❌ [MANIFEST CRASH] Validation failure. Missing fields: {missing_fields}")
            return None
            
        print(f"✅ [MANIFEST ENGINE] Intake processing successful for: {parsed_data.get('Core Intent')}")
        return parsed_data

    def generate_compact_system_prompt_addition(self, parsed_dict):
        """
        Formats extracted values into a compact, minimized layout envelope.
        Saves significant token window space compared to raw user text streams.
        """
        if not parsed_dict:
            return "CRITICAL: Invalid Manifest Parameter State."
            
        return (
            f"[SYSTEM DIRECTIVE MANIFEST]\n"
            f"TARGET_SYS: {parsed_dict.get('Target System')}\n"
            f"SCENARIO  : {parsed_dict.get('Scenario Type')}\n"
            f"INTENT    : {parsed_dict.get('Core Intent')}\n"
            f"DATA_LAYER: {parsed_dict.get('Target DB')}\n"
            f"POSTGRES  : {parsed_dict.get('Postgres EAV', 'None')}\n"
            f"CRITICAL  : Speak strictly in minimal layout directives and code snippets."
        )

if __name__ == "__main__":
    # Self-test trace execution verification hook
    STAGING_FILE = os.path.join(os.getcwd(), 'core_logic/staging/daily_brief.txt')
    parser = ManifestIntakeCore()
    
    # Pre-seed sample text array to check functional script loops cleanly
    os.makedirs(os.path.dirname(STAGING_FILE), exist_ok=True)
    with open(STAGING_FILE, 'w', encoding='utf-8') as f:
        f.write(
            "[FEATURE MANIFEST]\n"
            "Target System: Aurora\n"
            "Scenario Type: 1: New Feature\n"
            "Core Intent  : Implement automated local file cleaner logic matrix.\n"
            "Target DB    : PostgreSQL\n"
            "Postgres EAV : True\n"
        )
        
    result_dict = parser.load_manifest_from_staging(STAGING_FILE)
    if result_dict:
        compact_prompt = parser.generate_compact_system_prompt_addition(result_dict)
        print("\n🚀 --- COMPACT TOKEN-SAVER PROMPT ENVELOPE GEN ---")
        print(compact_prompt)
        print("--------------------------------------------------\n")
