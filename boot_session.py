# boot_session.py
import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_logic.settings')
django.setup()

# Clean imports: Removed unused datetime, timezone, Document, and Content
from aurora.models import Metadata
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def display_welcome_banner():
    banner_text = (
        "[bold cyan]AURORA AUTOMATION ECOSYSTEM v1.0 (MVP Active)[/bold cyan]\n"
        "[dim white]Host Environment Profile: Ubuntu Laptop | 2 Cores | 8GB RAM Profile[/dim white]"
    )
    console.print(Panel(banner_text, style="blue", expand=False))

def load_project_workspace(project_choice):
    project_key = "aurora" if project_choice == "1" else "hopehub"
    project_display = "AURORA DEVELOPMENT ENGINE" if project_key == "aurora" else "HOPEHUB HUMANITARIAN LAYER"
    
    console.print(f"\n[bold yellow]Booting Workspace Context Profile for: {project_display}...[/bold yellow]")
    
    # Gather active roadmap data tracks from relational Metadata tables
    roadmap_items = Metadata.objects.filter(key="roadmap_priority", status=project_key)
    
    table = Table(title=f"📋 Active Project Priorities & Roadmap Matrix: {project_key.upper()}")
    table.add_column("Task ID", style="cyan", no_wrap=True)
    table.add_column("Target Priority Component", style="white")
    table.add_column("Criticality", style="yellow")
    table.add_column("Status", style="green")
    
    if not roadmap_items.exists():
        # Fallback default seed priorities to keep the tracking table populated
        table.add_row("MVP-001", "Verify Rich Dynamic Router Monitor Panel Loops", "HIGH", "VERIFIED")
        table.add_row("MVP-002", "Deploy 0MB RAM Gemini Cloud-Embedding Vector Engine", "HIGH", "OPERATIONAL")
        table.add_row("MVP-003", "Initialize First Real-Life Code Generation Test Case", "HIGH", "TARGETED")
    else:
        for item in roadmap_items:
            table.add_row(item.type or "TASK", item.value, item.criticality or "MEDIUM", "PENDING")
            
    console.print(table)
    
    # Build the exact compilation prompt block needed to seed Wu's brain window
    print("\n" + "="*80)
    console.print(f"🧬 [bold green]COMPILED INITIALIZATION PROMPT FOR ORCHESTRATOR WU (70B)[/bold green]")
    print("="*80)
    
    wu_seed_prompt = (
        f"You are the Orchestrator Wu (Llama 3.3 70B). Current target context: {project_display.upper()}.\n"
        f"HARDWARE CONSTRAINTS: Ubuntu Laptop host interface, 2 Cores, 8GB RAM profile ceiling.\n"
        f"STORAGE BOUNDS: PostgreSQL local port 5432. Neo4j graph local port 7687.\n"
        f"OPERATIONAL DISK ROUTING CONSTRAINTS:\n"
        f"- Code changes must use the dynamic path parser tag layout: | FILE: path/to/target_file.ext\n"
        f"- Output raw code segments wrapped in language fences. Do not exceed the 4,500-token window constraints.\n"
        f"- All code drops must pass through the terminal display overlay logic in aurora.minion_array.router.\n\n"
        f"TARGETED RECENT DEVELOPMENT HISTORY:\n"
        f"- Localized databases cleanly to eliminate cloud Neon socket timeout errors.\n"
        f"- Deployed nano-vector search utilizing gemini-embedding-2 cloud models with 0MB local RAM bloat.\n"
        f"- Upgraded minion routing modules with rich panel tracing overlays and automated syntax verification traps.\n\n"
        f"CURRENT WORKSPACE PRIORITIES RIGHT NOW:\n"
        f"1. Pass Wu a real-life test case script operation to evaluate minion file-writing precision.\n"
        f"2. Maintain strict documentation logs on every code transformation via the Document EAV data engine.\n"
        f"Respond with: 'Wu Online. Standing by for specific module task instructions, Delta.'"
    )
    
    print(wu_seed_prompt)
    print("="*80 + "\n")
    
    # Save the current state tracking data locally to ensure the text layer is preserved
    state_path = os.path.join(os.getcwd(), "PROJECT_STATE.md")
    with open(state_path, "w", encoding="utf-8") as f:
        f.write(f"# Target System Active Profile: {project_key.upper()}\n\n{wu_seed_prompt}")
    console.print(f"✔ Workspace session files refreshed. Initial state cached inside: {state_path}\n", style="bold green")

def main():
    display_welcome_banner()
    print("Select target project development workspace to initialize:")
    print("  1. AURORA (Developer Automation Systems & Minion Orchestration)")
    print("  2. HOPEHUB (Humanitarian Layers - Food, Housing, Financial Systems)")
    
    choice = input("\nEnter system selection token (1 or 2): ").strip()
    if choice in ["1", "2"]:
        load_project_workspace(choice)
    else:
        console.print("[ERROR] Invalid choice token selection. Boot protocol terminated.", style="bold red")

if __name__ == "__main__":
    main()
