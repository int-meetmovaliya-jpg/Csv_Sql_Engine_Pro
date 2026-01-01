import os
import json
from datetime import datetime

SCHEMAS_DIR = "schemas"

def save_schema_version(con, table_name):
    os.makedirs(SCHEMAS_DIR, exist_ok=True)
    try:
        schema_info = con.execute(f"DESCRIBE {table_name}").fetchall()
        # Convert to list of dicts
        schema_dict = [{"column": r[0], "type": r[1], "nullable": r[2]} for r in schema_info]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{table_name}_{timestamp}.json"
        
        with open(os.path.join(SCHEMAS_DIR, filename), "w") as f:
            json.dump(schema_dict, f, indent=4)
            
        return filename
    except Exception as e:
        print(f"Error saving schema: {e}")
        return None

def list_schema_versions():
    if not os.path.exists(SCHEMAS_DIR):
        return []
    return sorted(os.listdir(SCHEMAS_DIR), reverse=True)
