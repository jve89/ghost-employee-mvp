import os
import json
import sys
from rich.console import Console
from rich.prompt import Prompt
from src.processing.task_executor import execute_task

LOGS_FOLDER = "logs"
EXECUTED_FOLDER = "executed"
MAPPINGS_FILE = "manual_mappings.json"
console = Console()

# Load manual mappings (if any)
if os.path.exists(MAPPINGS_FILE):
    with open(MAPPINGS_FILE) as f:
        manual_mappings = json.load(f)
else:
    manual_mappings = {}

def load_structured_logs():
    files = [f for f in os.listdir(LOGS_FOLDER) if f.startswith("structured_") and f.endswith(".json")]
    files.sort()
    logs = []
    for f in files:
        path = os.path.join(LOGS_FOLDER, f)
        with open(path) as file:
            try:
                data = json.load(file)
                logs.append((f, data))
            except Exception as e:
                console.print(f"[red]Error loading {f}: {e}[/red]")
    return logs

def has_been_executed(structured_name):
    base = structured_name.replace("structured_", "").replace(".json", "")
    for f in os.listdir(EXECUTED_FOLDER):
        if f.startswith(f"exec_{base}"):
            return True
    return False

def review_tasks(recheck_all=False):
    logs = load_structured_logs()
    if not logs:
        console.print("[bold green]✅ No structured logs found.[/bold green]")
        return

    reviewed_any = False
    for filename, data in logs:
        if not recheck_all and (not data.get("tasks") or has_been_executed(filename)):
            continue

        console.rule(f"📄 {filename}")
        console.print(f"[bold]Summary:[/bold]\n{data.get('summary', '')}")

        updated_tasks = []
        tasks = data.get("tasks", [])
        for idx, task in enumerate(tasks):
            console.print(f"\n[bold yellow]Task {idx+1}:[/bold yellow] {task}")
            default = "s" if task not in manual_mappings else "m"
            action = Prompt.ask("Choose", choices=["e", "s", "r", "m", "x"], default=default, show_choices=False)

            if action == "e":
                console.print("[cyan]Executing...[/cyan]")
                result = execute_task(task, source_file=filename)
                console.print(f"[green]✓ Result:[/green] {result['result']}")

            elif action == "m":
                console.print("[magenta]Marked as manually handled.[/magenta]")
                updated_tasks.append({"task": task, "status": "manual"})

            elif action == "x":
                console.print("[grey]Skipped (left for later).[/grey]")
                updated_tasks.append({"task": task, "status": "skipped"})
                continue

            elif action == "r":
                console.print("[blue]Marked as reviewed (no action taken).[/blue]")
                updated_tasks.append({"task": task, "status": "reviewed"})

            elif action == "s":
                chosen = Prompt.ask("Which function to assign?", choices=[
                    "create_jira_ticket", "update_google_sheet", "assign_task_in_clickup",
                    "email_hr", "create_calendar_event_flexible", "send_slack_message",
                    "update_crm_case", "email_supervisor", "fallback_action"
                ])
                console.print(f"[cyan]Simulating execution of: {chosen}...[/cyan]")
                result = execute_task(task, source_file=filename, override_fn=chosen)
                console.print(f"[green]✓ Simulated Result:[/green] {result['result']}")
                manual_mappings[task] = chosen
                updated_tasks.append({"task": task, "status": f"mapped to {chosen}"})
            reviewed_any = True

        # Save mappings if new
        with open(MAPPINGS_FILE, "w") as f:
            json.dump(manual_mappings, f, indent=2)

        console.rule("[dim]End of Log\n")

    if not reviewed_any:
        console.print("[bold green]✅ No logs needed review.[/bold green]")

if __name__ == "__main__":
    recheck = "--all" in sys.argv or "-a" in sys.argv
    review_tasks(recheck_all=recheck)
