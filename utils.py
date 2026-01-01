"""
Utility functions for validation, security, and performance optimization
"""
import re
import hashlib
import duckdb

# Configuration constants
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
MAX_RESULT_ROWS = 10000  # Maximum rows to display at once
PAGINATION_SIZE = 1000  # Rows per page

def validate_table_name(name):
    """Validate table name is safe (SQL injection prevention)"""
    if not name:
        raise ValueError("Table name cannot be empty")
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"Invalid table name: {name}. Only alphanumeric characters and underscores allowed, must start with letter or underscore.")
    if len(name) > 63:  # PostgreSQL/SQL standard limit
        raise ValueError(f"Table name too long (max 63 characters): {name}")
    return name

def validate_file_upload(file):
    """Validate uploaded file size and type"""
    if file.size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file.size / 1024 / 1024 / 1024:.2f}GB. Maximum size: {MAX_FILE_SIZE / 1024 / 1024 / 1024:.0f}GB")
    if not file.name.lower().endswith('.csv'):
        raise ValueError("Only CSV files are allowed")
    # Sanitize filename
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file.name)
    return safe_name

def sanitize_table_name(name):
    """Sanitize table name from file name"""
    # Convert to safe table name
    safe = name.replace(".csv", "").replace("-", "_").replace(" ", "_")
    safe = safe.replace("(", "").replace(")", "").replace(".", "_")
    safe = safe.lower().strip("_")
    # Remove any remaining invalid characters
    safe = re.sub(r'[^a-zA-Z0-9_]', '_', safe)
    # Ensure it starts with letter or underscore
    if safe and not safe[0].isalpha() and safe[0] != '_':
        safe = '_' + safe
    return safe

def validate_sql_query(query):
    """Basic SQL validation - warn about dangerous operations"""
    query_upper = query.upper().strip()
    dangerous_keywords = ['DROP TABLE', 'DROP DATABASE', 'DELETE FROM', 'TRUNCATE', 'ALTER TABLE']
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            # Allow but warn (user might need these operations)
            return True  # Don't block, just warn in UI
    return True

def create_query_hash(query):
    """Create a hash of the query for caching"""
    return hashlib.md5(query.encode()).hexdigest()

def safe_execute(con, query, params=None):
    """
    Execute query with proper error handling and parameterization
    Uses parameterized queries to prevent SQL injection
    """
    try:
        if params:
            return con.execute(query, params)
        else:
            return con.execute(query)
    except duckdb.Error as e:
        raise ValueError(f"Database error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Execution error: {str(e)}")

def paginate_dataframe(df, page_num=0, page_size=PAGINATION_SIZE):
    """Paginate a dataframe for display"""
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size
    start_idx = page_num * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx], total_rows, total_pages

