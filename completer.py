from prompt_toolkit.completion import Completer, Completion
import re

SQL_KEYWORDS = [
    "select", "from", "where", "group by", "order by",
    "join", "left join", "right join", "inner join",
    "create", "or replace", "table", "drop", "union", "all",
    "window", "over", "partition by", "limit",
    "having", "distinct", "as", "on"
]

SQL_FUNCTIONS = [
    "count", "sum", "avg", "min", "max",
    "row_number", "rank", "dense_rank",
    "lag", "lead", "coalesce"
]

SQL_MACROS = [
    "@top_users",
    "@daily_agg",
    "@dedup_latest"
]


class SQLCompleter(Completer):
    def __init__(self, duckdb_connection):
        self.con = duckdb_connection

    def get_tables(self):
        try:
            rows = self.con.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='main'
            """).fetchall()
            return [r[0] for r in rows]
        except:
            return []

    def get_columns(self, table):
        try:
            rows = self.con.execute(f"DESCRIBE {table}").fetchall()
            return [r[0] for r in rows]
        except:
            return []

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower()
        word = document.get_word_before_cursor()

        suggestions = set()

        # Always suggest keywords, functions, macros
        suggestions.update(SQL_KEYWORDS)
        suggestions.update(SQL_FUNCTIONS)
        suggestions.update(SQL_MACROS)

        tables = self.get_tables()
        suggestions.update(tables)

        # Context-aware: after FROM / JOIN → tables
        if re.search(r"(from|join)\s+$", text):
            suggestions = set(tables)

        # Context-aware: after table.column
        match = re.search(r"(\w+)\.(\w*)$", text)
        if match:
            table = match.group(1)
            cols = self.get_columns(table)
            for c in cols:
                yield Completion(
                    c,
                    start_position=-len(match.group(2))
                )
            return

        # Yield normal suggestions
        for s in sorted(suggestions):
            if s.startswith(word.lower()):
                yield Completion(
                    s,
                    start_position=-len(word)
                )
