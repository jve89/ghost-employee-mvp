import os
import json
from rich.console import Console
from rich.table import Table
from rich.text import Text
from datetime import datetime

EXECUTED_DIR = "executed"
console = Console()

def load_executed_logs():
    files = [f for f in os.listdir(EXECUTED_DIR) if f.endswith(".json")]
    files.sort(reverse=True)
    logs = []

    for file in files:
        try:
            with open(os.path.join(EXECUTED_DIR, file), "r") as f:
                data = json.load(f)
                # Only accept well-structured logs
                if all(k in data for k in ["task", "result", "mode", "timestamp"]):
                    logs.append(data)
                else:
                    console.print(f"[yellow]Skipping malformed log: {file}[/yellow]")
        except Exception as e:
            console.print(f"[red]Error reading {file}: {e}[/red]")

    return logs

def style_result(result_text):
    """Colour-code result keywords like FAIL/ALERT"""
    result_upper = result_text.upper()

    if any(word in result_upper for word in ["FAIL", "ERROR", "ALERT"]):
        return Text(result_text, style="bold red")
    if "SIMULATED" in result_upper:
        return Text(result_text, style="green")
    if "REAL" in result_upper:
        return Text(result_text, style="bold magenta")
    return Text(result_text)

def show_summary_stats(logs):
    simulated = sum(1 for log in logs if log["mode"] == "SIMULATED")
    real = sum(1 for log in logs if log["mode"] == "REAL")

    console.print(f"\n[bold blue]Total logs:[/bold blue] {len(logs)}")
    console.print(f"🧪 [green]SIMULATED:[/green] {simulated}    🚀 [magenta]REAL:[/magenta] {real}\n")

def show_dashboard(logs, filter_mode=None, keyword_filter=None):
    filtered_logs = []

    for log in logs:
        if filter_mode and log["mode"].upper() != filter_mode:
            continue
        if keyword_filter and keyword_filter not in log["task"].lower() and keyword_filter not in log["result"].lower():
            continue
        filtered_logs.append(log)

    if not filtered_logs:
        console.print("[yellow]No matching logs found.[/yellow]")
        return

    show_summary_stats(filtered_logs)

    table = Table(title="📊 Ghost Employee – Executed Task Log", show_lines=True)

    table.add_column("Timestamp", style="cyan", width=22)
    table.add_column("Task", style="white", overflow="fold", max_width=40)
    table.add_column("Result", style="green")
    table.add_column("Mode", style="magenta")
    table.add_column("Source File", style="yellow")

    for log in filtered_logs:
        table.add_row(
            log.get("timestamp", "N/A"),
            log.get("task", "N/A"),
            style_result(log.get("result", "N/A")),
            log.get("mode", "N/A"),
            log.get("source_file", "N/A"),
        )

    console.print(table)

def main():
    logs = load_executed_logs()

    if not logs:
        console.print("[bold red]No execution logs found in /executed/[/bold red]")
        return

    console.print("\n[bold blue]Filter options:[/bold blue] [green]SIMULATED[/green], [magenta]REAL[/magenta], or leave blank to show all")
    filter_mode = console.input("Enter filter mode (optional): ").strip().upper()
    if filter_mode == "":
        filter_mode = None

    keyword_filter = console.input("Enter keyword filter (optional, e.g. 'jira', 'failed'): ").strip().lower()
    if keyword_filter == "":
        keyword_filter = None

    show_dashboard(logs, filter_mode, keyword_filter)

if __name__ == "__main__":
    main()
