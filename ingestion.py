import os
import duckdb
from rich import print

def ingest_csv(con, path):
    if not os.path.exists(path):
        print(f"[red]Error: Path {path} does not exist.[/red]")
        return None
    
    table_name = os.path.splitext(os.path.basename(path))[0].lower()
    table_name = table_name.replace("-", "_").replace(" ", "_")

    try:
        con.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{path}')
        """)
        print(f"[green]Successfully loaded {path} into table '{table_name}'[/green]")
        return table_name
    except Exception as e:
        print(f"[red]Failed to ingest {path}: {e}[/red]")
        return None

def auto_ingest_folder(con, folder_path):
    if not os.path.exists(folder_path):
        return []
    
    loaded_tables = []
    for f in os.listdir(folder_path):
        if f.endswith(".csv"):
            table = ingest_csv(con, os.path.join(folder_path, f))
            if table:
                loaded_tables.append(table)
    return loaded_tables
