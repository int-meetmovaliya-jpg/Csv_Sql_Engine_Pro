import duckdb
import os
from rich import print

class SQLEngine:
    def __init__(self, db_file="metadata.db"):
        self.db_file = db_file
        self.con = duckdb.connect(db_file)
        print(f"[dim]Connected to DuckDB: {db_file}[/dim]")

    def execute(self, sql):
        return self.con.execute(sql)

    def get_connection(self):
        return self.con

    def list_tables(self):
        return self.con.execute("SHOW TABLES").fetchall()
