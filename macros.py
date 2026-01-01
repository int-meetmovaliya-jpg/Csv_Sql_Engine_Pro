import re

MACRO_MAP = {
    "@top_users": "SELECT user_id, count(*) as cnt FROM sales GROUP BY user_id ORDER BY cnt DESC LIMIT 10",
    "@daily_agg": "SELECT date_trunc('day', timestamp) as day, sum(amount) as total FROM sales GROUP BY 1 ORDER BY 1",
    "@dedup_latest": "SELECT * FROM (SELECT *, row_number() OVER (PARTITION BY id ORDER BY updated_at DESC) as rn FROM my_table) WHERE rn = 1"
}

def expand_macros(sql):
    for macro, replacement in MACRO_MAP.items():
        if macro in sql:
            sql = sql.replace(macro, f"({replacement})")
    return sql
