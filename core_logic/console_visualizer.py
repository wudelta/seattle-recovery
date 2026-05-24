import sys
import os
import time

class AuroraTerminalConsole:
    """
    High-Utility, Headless Terminal Monitoring Dashboard for Project Aurora.
    Displays Token Burn Rates, Database Status, and Background Minion Pipeline Tasks.
    """
    def __init__(self):
        # ANSI Escape Codes for Scannable Visual Formatting
        self.CLR_RESET = "\033[0m"
        self.CLR_GREEN = "\033[92m"
        self.CLR_YELLOW = "\033[93m"
        self.CLR_RED = "\033[91m"
        self.CLR_CYAN = "\033[96m"
        self.CLR_BOLD = "\033[1m"

    def calculate_burn_rate(self, tokens_used, limit=14400):
        """Computes current token usage safety percentage."""
        if limit <= 0:
            return 0.0
        return min(100.0, (tokens_used / limit) * 100)

    def draw_progress_bar(self, percentage):
        """Generates a text-based high-density progress bar block."""
        slots = 20
        filled_slots = int(percentage / (100 / slots))
        
        if percentage > 75:
            color = self.CLR_RED
        elif percentage > 50:
            color = self.CLR_YELLOW
        else:
            color = self.CLR_GREEN
            
        bar = "█" * filled_slots + " " * (slots - filled_slots)
        return f"[{color}{bar}{self.CLR_RESET}] {percentage:.1f}%"

    def render_dashboard(self, session_metrics: dict, current_task: dict):
        """Renders the complete operational state system to the command line console."""
        # Clear screen for dynamic terminal rendering updates
        os.system('cls' if os.name == 'nt' else 'clear')
        
        tokens_consumed = session_metrics.get("prompt_tokens", 0) + session_metrics.get("completion_tokens", 0)
        token_limit = session_metrics.get("token_limit", 14400)
        burn_pct = self.calculate_burn_rate(tokens_consumed, token_limit)
        
        print(f"{self.CLR_CYAN}{self.CLR_BOLD}" + "="*65 + f"{self.CLR_RESET}")
        print(f"⚡ {self.CLR_BOLD}PROJECT AURORA{self.CLR_RESET} :: CORE TERMINAL ORCHESTRATION CONSOLE")
        print(f"{self.CLR_CYAN}" + "="*65 + f"{self.CLR_RESET}")
        
        # Operational Profiles Tracking Block
        print(f"👤 {self.CLR_BOLD}Identity Context{self.CLR_RESET}    : {session_metrics.get('user_id', 'DELTA').upper()}")
        print(f"⏱️  Active Workspace   : {session_metrics.get('session_duration', '0s')}")
        print(f"🗄️  Postgres Storage   : {session_metrics.get('postgres_status', 'CONNECTED')}")
        print(f"📊  Neo4j Graph State  : {session_metrics.get('neo4j_nodes', 0)} raw chat nodes tracked")
        print("-"*65)
        
        # Token Saving Boundary Visualizers
        print(f"🎟️  {self.CLR_BOLD}Groq Context Runway Capacity Burn Rate:{self.CLR_RESET}")
        print(f"   {self.draw_progress_bar(burn_pct)}")
        print(f"   Tokens Burnt: {tokens_consumed} / Ceiling Allowance: {token_limit}")
        print("-"*65)
        
        # Mechanical Layer Worker Tracking
        print(f"⚙️  {self.CLR_BOLD}ACTIVE PIPELINE TRANSACTION METRIC:{self.CLR_RESET}")
        print(f"   Task Target : {current_task.get('target', 'IDLE')}")
        print(f"   Active Phase: {current_task.get('phase', 'PENDING MANIFEST INTAKE')}")
        
        status = current_task.get('status', 'IDLE')
        if "❌" in status or "FAIL" in status:
            status_color = self.CLR_RED
        elif "✅" in status or "SUCCESS" in status:
            status_color = self.CLR_GREEN
        else:
            status_color = self.CLR_YELLOW
            
        print(f"   Trace Status: {status_color}{status}{self.CLR_RESET}")
        print(f"{self.CLR_CYAN}" + "="*65 + f"{self.CLR_RESET}\n")

if __name__ == "__main__":
    # Test script initialization loop to inspect display behavior locally
    console = AuroraTerminalConsole()
    
    mock_metrics = {
        "user_id": "delta",
        "session_duration": "14m 35s",
        "postgres_status": "ONLINE (TEST_DB)",
        "neo4j_nodes": 2,
        "prompt_tokens": 6200,
        "completion_tokens": 1450,
        "token_limit": 14400
    }
    
    mock_task = {
        "target": "aurora/views/start_online_session.py",
        "phase": "STAGE 3: Computing offline session planning metrics",
        "status": "✅ SUCCESS: Timezone-aware timestamp match verified."
    }
    
    console.render_dashboard(mock_metrics, mock_task)
