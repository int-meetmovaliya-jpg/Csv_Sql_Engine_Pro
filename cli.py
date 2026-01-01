import os
import sys
from prompt_toolkit import PromptSession
from rich import print
from rich.table import Table
from rich.console import Console

# Import local modules
from engine import SQLEngine
from completer import SQLCompleter
from ingestion import ingest_csv, auto_ingest_folder
from macros import expand_macros
from versioning import save_schema_version

console = Console()

def main():
    print("[bold cyan]CSV SQL Engine (Local Databricks Style)[/bold cyan]\n")
    
    engine = SQLEngine()
    con = engine.get_connection()
    
    # ---- AUTO INGEST FROM data/ ----
    auto_ingest_folder(con, "data")

    # ---- CSV INGESTION MANUALLY ----
    print("\n[yellow]Manually ingest CSV files? (Press ENTER to skip)[/yellow]")
    while True:
        path = input("Paste CSV path: ").strip()
        if not path:
            break
        table = ingest_csv(con, path)
        if table:
            save_schema_version(con, table)

    # ---- SQL MODE ----
    session = PromptSession(
        completer=SQLCompleter(con),
        complete_while_typing=True
    )

    print("\n[green]SQL Mode Started (type 'exit' or 'quit' to stop)[/green]")
    print("[dim]Macros supported: @top_users, @daily_agg, @dedup_latest[/dim]\n")

    while True:
        try:
            sql = session.prompt("sql> ").strip()
            if not sql:
                continue
            if sql.lower() in ("exit", "quit"):
                break

            # Expand macros
            expanded_sql = expand_macros(sql)
            if expanded_sql != sql:
                print(f"[dim]Expanded SQL: {expanded_sql}[/dim]")

            result = con.execute(expanded_sql)

            if result.description:
                # Use Rich to display a nice table
                columns = [desc[0] for desc in result.description]
                rows = result.fetchall()
                
                table = Table(show_header=True, header_style="bold magenta")
                for col in columns:
                    table.add_column(col)
                
                # Show top 20 rows
                for r in rows[:20]:
                    table.add_row(*[str(val) for val in r])
                
                console.print(table)
                print(f"[dim]{len(rows)} rows total (showing top 20)[/dim]")
            else:
                print("[green]Command executed successfully.[/green]")

        except Exception as e:
            print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
