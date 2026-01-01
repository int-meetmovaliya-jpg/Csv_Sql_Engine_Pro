import streamlit as st
import duckdb
import pandas as pd
import os
from datetime import datetime
import re
from streamlit_ace import st_ace

# --- Page Config ---
st.set_page_config(
    page_title="CSV SQL Engine Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'notebooks' not in st.session_state:
    st.session_state.notebooks = {
        "Main Analytics": [{"id": 0, "query": "SELECT * FROM sales LIMIT 10", "result": None, "meta": {}}]
    }
if 'current_notebook' not in st.session_state:
    st.session_state.current_notebook = "Main Analytics"
if 'pending_files' not in st.session_state:
    st.session_state.pending_files = {}
if 'editing_file' not in st.session_state:
    st.session_state.editing_file = None
if 'managing_table' not in st.session_state:
    st.session_state.managing_table = None
if 'active_tool' not in st.session_state:
    st.session_state.active_tool = None

# --- Custom Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #f8fafc !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.5);
    }

    /* Sidebar specific button overrides */
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        color: #94a3b8 !important;
    }

    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(59, 130, 246, 0.1) !important;
        border-color: #3b82f6 !important;
        color: #f8fafc !important;
    }

    [data-testid="stSidebar"] .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
    }

    .notebook-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 2rem;
    }

    .cell-index {
        font-family: 'JetBrains Mono', monospace;
        color: #94a3b8;
        font-weight: bold;
        margin-bottom: 8px;
    }

    .ace_editor {
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
    }
    
    .table-container {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 30px;
    }

    .progress-styled {
        height: 3px;
        background: linear-gradient(90deg, #3b82f6 0%, transparent 100%);
        border-radius: 2px;
        margin-bottom: 20px;
    }

    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .status-live { background: rgba(34, 197, 94, 0.1); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.2); }
    .status-locked { background: rgba(234, 179, 8, 0.1); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.2); }

    .copy-btn {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #94a3b8;
        border-radius: 8px;
        padding: 6px;
        width: 100%;
        height: 38px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }

    .copy-btn:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: #3b82f6;
        color: #f8fafc;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- Database Setup ---
if 'con' not in st.session_state:
    try:
        st.session_state.con = duckdb.connect("metadata.db", read_only=False)
        st.session_state.read_only = False
    except:
        st.session_state.con = duckdb.connect(":memory:")
        st.session_state.read_only = True
    
    # --- OPTIMIZED HARDWARE TUNING (No-Lag Mode) ---
    st.session_state.con.execute("SET memory_limit='10GB'")
    st.session_state.con.execute("SET threads=4") # Balanced for smooth multitasking (Prevents Laptop Lag)
    st.session_state.con.execute("SET preserve_insertion_order=false")
    st.session_state.con.execute("SET max_temp_directory_size='500GB'")
    st.session_state.con.execute("SET allocator_flush_threshold='128MB'") # Keeps memory lean
    
    # --- SMART FAST-START LOGIC ---
    # Only ingest CSVs that aren't already in our persistent metadata.db
    if os.path.exists("data"):
        existing_tables = [t[0].lower() for t in st.session_state.con.execute("SHOW TABLES").fetchall()]
        for f in os.listdir("data"):
            if f.endswith(".csv"):
                t_name = f.replace(".csv", "").replace("-", "_").replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_").lower().strip("_")
                if t_name not in existing_tables:
                    try: 
                        st.session_state.con.execute(f"CREATE TABLE {t_name} AS SELECT * FROM read_csv_auto('data/{f}')")
                        st.session_state.con.execute(f"ANALYZE {t_name}") # Pre-calculate statistics for fast JOINs
                    except: pass
    
    st.session_state.con.execute("CHECKPOINT") # Persist and compact

con = st.session_state.con

# --- Helper Functions ---
def get_active_cells():
    return st.session_state.notebooks.get(st.session_state.current_notebook, [])

def add_cell():
    active_cells = get_active_cells()
    new_id = max([c["id"] for c in active_cells]) + 1 if active_cells else 0
    active_cells.append({"id": new_id, "query": "", "result": None, "meta": {}})

def delete_cell(idx):
    active_cells = get_active_cells()
    if len(active_cells) > 1:
        active_cells.pop(idx)
        st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/database.png", width=80)
    st.title("Settings")
    
    st.divider()
    
    # 🤖 Mini Apps
    st.header("🤖 Smart Tools")
    if st.button("🤝 Common Finder", use_container_width=True, type="primary" if st.session_state.active_tool == "common_finder" else "secondary"):
        st.session_state.active_tool = "common_finder"
        st.session_state.editing_file = None
        st.session_state.managing_table = None
        st.rerun()
    
    # � Notebook List
    st.header("📓 Notebooks")
    new_nb = st.text_input("New Notebook", placeholder="Enter name...", key="side_new_nb")
    if st.button("➕ Create", use_container_width=True):
        if new_nb and new_nb not in st.session_state.notebooks:
            st.session_state.notebooks[new_nb] = [{"id": 0, "query": "", "result": None, "meta": {}}]
            st.session_state.current_notebook = new_nb
            st.rerun()

    st.write("")
    for nb in list(st.session_state.notebooks.keys()):
        c1, c2 = st.columns([0.8, 0.2])
        is_active = (nb == st.session_state.current_notebook)
        if c1.button(f"📄 {nb}", key=f"nb_sel_{nb}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.current_notebook = nb
            st.session_state.editing_file = None
            st.session_state.managing_table = None
            st.session_state.active_tool = None
            st.rerun()
        if nb != "Main Analytics":
            if c2.button("🗑️", key=f"nb_del_{nb}", use_container_width=True):
                del st.session_state.notebooks[nb]
                if st.session_state.current_notebook == nb:
                    st.session_state.current_notebook = list(st.session_state.notebooks.keys())[0]
                st.rerun()

    st.divider()

    # 🔍 Schema Explorer (The "Robust" Recommendation Tool)
    st.header("🔍 Schema Reference")
    search_q = st.text_input("Search tables or columns...", placeholder="Find schema...", key="schema_search").lower()
    
    try:
        # Get all table/column data (ordered by position for better understanding)
        schema_data = con.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'main'
            ORDER BY table_name, ordinal_position
        """).fetchall()
        
        # Organize into dict: {table: [(col, type), ...]}
        schema_tree = {}
        for tn, cn, dt in schema_data:
            if tn not in schema_tree: schema_tree[tn] = []
            schema_tree[tn].append((cn, dt))
            
        for tn, cols in schema_tree.items():
            # Filter based on search
            matching_cols = [c for c in cols if search_q in tn or search_q in c[0].lower()]
            if search_q and not matching_cols: continue
            
            with st.expander(f"📁 {tn}"):
                # Table Name Copy
                tc_1, tc_2 = st.columns([0.8, 0.2])
                tc_1.caption("Table Name")
                tc_2.markdown(f"""
                    <button class="copy-btn" style="height:25px; font-size:0.8rem;" 
                        onclick="(function(v, b) {{
                            const e = document.createElement('textarea');
                            e.value = v; e.style.position = 'fixed'; e.style.opacity = '0';
                            b.parentNode.appendChild(e); e.select();
                            document.execCommand('copy');
                            b.parentNode.removeChild(e);
                            const old = b.innerText; b.innerText = '✅';
                            setTimeout(() => {{ b.innerText = old; }}, 1000);
                        }})('{tn}', this)">
                        📋
                    </button>
                """, unsafe_allow_html=True)
                
                st.divider()
                for cn, dt in cols:
                    if search_q and search_q not in cn.lower() and search_q not in tn: continue
                    cc_1, cc_2 = st.columns([0.8, 0.2])
                    cc_1.markdown(f"`{cn}` <small style='color:#64748b'>{dt}</small>", unsafe_allow_html=True)
                    cc_2.markdown(f"""
                        <button class="copy-btn" style="height:25px; font-size:0.8rem;" 
                            onclick="(function(v, b) {{
                                const e = document.createElement('textarea');
                                e.value = v; e.style.position = 'fixed'; e.style.opacity = '0';
                                b.parentNode.appendChild(e); e.select();
                                document.execCommand('copy');
                                b.parentNode.removeChild(e);
                                const old = b.innerText; b.innerText = '✅';
                                setTimeout(() => {{ b.innerText = old; }}, 1000);
                            }})('{cn}', this)">
                            📋
                        </button>
                    """, unsafe_allow_html=True)
    except: st.write("No tables to explore.")

    st.divider()

    # 📥 Ingestion
    st.header("📥 Ingest Data")
    uploads = st.file_uploader("Upload CSV", type=["csv"], accept_multiple_files=True, label_visibility="collapsed")
    
    # Process new uploads
    if uploads:
        for f in uploads:
            if f.name not in st.session_state.pending_files:
                try:
                    # 1. Save to disk immediately (Safe for 5GB+ and fixes LogicalType Error)
                    os.makedirs("data", exist_ok=True)
                    f_path = os.path.join("data", f.name)
                    with open(f_path, "wb") as tmp_f:
                        tmp_f.write(f.getbuffer())
                    
                    # 2. Get Preview from Disk using Path (Robust)
                    df_p = con.execute("SELECT * FROM read_csv_auto(?) LIMIT 10", [f_path]).df()
                    
                    st.session_state.pending_files[f.name] = {
                        "path": f_path, 
                        "columns": list(df_p.columns), 
                        "preview": df_p,
                        "table_name": f.name.replace(".csv", "").replace("-", "_").replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_").lower().strip("_")
                    }
                    st.toast(f"🚚 {f.name} saved to disk & ready!")
                except Exception as e:
                    st.error(f"Failed to read {f.name}: {e}")

    # Always show Pending if anything is there
    if st.session_state.pending_files:
        st.write("---")
        st.subheader("📝 Pending Action")
        
        # Action to clear out stuck files
        if st.button("🧹 Clear All Pending", use_container_width=True):
            st.session_state.pending_files = {}
            st.rerun()
            
        for fn in list(st.session_state.pending_files.keys()):
            info = st.session_state.pending_files[fn]
            p_col1, p_col2, p_col3 = st.columns([0.5, 0.25, 0.25])
            p_col1.caption(fn)
            
            # Config Button
            if p_col2.button("🛠️", key=f"cfg_{fn}", use_container_width=True, help="Configure & Import"):
                st.session_state.editing_file = fn
                st.session_state.managing_table = None
                st.rerun()
                
            # Quick Ingest
            if p_col3.button("⚡", key=f"qik_{fn}", use_container_width=True, help="Fast Ingest"):
                try:
                    tn = info["table_name"]
                    # Use path string to avoid TypeErrors
                    con.execute(f'CREATE OR REPLACE TABLE "{tn}" AS SELECT * FROM read_csv_auto(?)', [info["path"]])
                    
                    # Auto-Index
                    for c in info["columns"]:
                        if any(k in c.lower() for k in ["id", "num", "phone", "email"]):
                            try: con.execute(f'CREATE INDEX IF NOT EXISTS idx_{tn}_{c} ON "{tn}"("{c}")')
                            except: pass
                    
                    del st.session_state.pending_files[fn]
                    st.toast(f"✅ Created table: {tn}")
                    st.rerun()
                except Exception as e_q:
                    st.error(f"Quick load failed: {e_q}")

    st.divider()

    # 🗂️ Active Tables
    st.header("🗂️ Tables")
    
    try:
        tbls = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
        st.write("")
        for t in tbls:
            tc1, tc2, tc3 = st.columns([0.7, 0.15, 0.15])
            
            # Label/Manage
            if tc1.button(f"📊 {t}", key=f"tbl_view_{t}", use_container_width=True):
                st.session_state.managing_table = t
                st.session_state.editing_file = None
            
            # Direct Copy Button (HTML/JS - No Rerun, Preserves State)
            with tc2:
                st.markdown(f"""
                    <button class="copy-btn" 
                        onclick="(function(v, b) {{
                            const e = document.createElement('textarea');
                            e.value = v; e.style.position = 'fixed'; e.style.opacity = '0';
                            b.parentNode.appendChild(e); e.select();
                            document.execCommand('copy');
                            b.parentNode.removeChild(e);
                            const old = b.innerText; b.innerText = '✅';
                            setTimeout(() => {{ b.innerText = old; }}, 1000);
                        }})('{t}', this)" 
                        title="Copy to clipboard">
                        📋
                    </button>
                """, unsafe_allow_html=True)
            
            # Drop
            if tc3.button("🗑️", key=f"tbl_drop_{t}", use_container_width=True):
                try:
                    # 1. Drop from database
                    con.execute(f'DROP TABLE IF EXISTS "{t}"')
                    
                    # 2. Clean up backend storage (data/ folder)
                    if os.path.exists("data"):
                        for f in os.listdir("data"):
                            base_name = f.replace(".csv", "").replace("-", "_").replace(" ", "_").lower()
                            if base_name == t.lower() or f.lower() == f"{t.lower()}.csv":
                                try: os.remove(os.path.join("data", f))
                                except: pass
                    
                    # 3. Toast notification and Rerun
                    st.toast(f"✅ Table '{t}' deleted successfully!")
                    st.rerun()
                except Exception as e_drop:
                    st.error(f"Failed to delete table: {e_drop}")
    except Exception as e_list:
        st.error(f"⚠️ Table list could not be loaded: {e_list}")

# --- Main Workspace ---

# 1. Schema Editor
if st.session_state.editing_file:
    fn = st.session_state.editing_file
    info = st.session_state.pending_files[fn]
    st.markdown(f"## 🛠️ Schema Editor: {fn}")
    with st.container():
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.subheader("Preview")
        st.dataframe(info["preview"], use_container_width=True, hide_index=True)
        st.divider()
        
        t_target = st.text_input("Table Name", value=info["table_name"])
        st.write("**Column Mapping**")
        renames = {}
        cols = st.columns(3)
        for i, c in enumerate(info["columns"]):
            with cols[i % 3]: renames[c] = st.text_input(c, value=c, key=f"ren_{fn}_{c}")
            
        st.divider()
        rc1, rc2 = st.columns(2)
        if rc1.button("🚀 Ingest Now", use_container_width=True, type="primary"):
            try:
                # 1. Create table with renames in DuckDB (using disk path)
                expr = ", ".join([f'"{old}" AS "{new}"' for old, new in renames.items()])
                con.execute(f'CREATE OR REPLACE TABLE "{t_target}" AS SELECT {expr} FROM read_csv_auto(?)', [info["path"]])
                
                # 2. Persist to backend CSV
                os.makedirs("data", exist_ok=True)
                target_path = os.path.join("data", f"{t_target}.csv")
                con.execute(f'COPY "{t_target}" TO \'{target_path}\' (HEADER, DELIMITER \',\')')
                
                # 3. Auto-indexing for performance (Robust Optimization)
                for old, new in renames.items():
                    col_low = new.lower()
                    if any(key in col_low for key in ["id", "num", "phone", "email", "code", "key"]):
                        try:
                            con.execute(f'CREATE INDEX IF NOT EXISTS idx_{t_target}_{col_low} ON "{t_target}"("{new}")')
                        except: pass
                
                # 4. Cleanup session state
                from versioning import save_schema_version
                save_schema_version(con, t_target)
                del st.session_state.pending_files[fn]
                st.session_state.editing_file = None
                st.toast(f"✨ {t_target} ingested and optimized for performance!")
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")
        if rc2.button("Cancel", use_container_width=True):
            st.session_state.editing_file = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 3. Mini App: Common Value Finder
elif st.session_state.active_tool == "common_finder":
    st.markdown("## 🤝 Smart Common Value Finder")
    st.caption("Automatically detects common columns and finds overlapping records between two datasets.")
    
    try:
        tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
        if len(tables) < 2:
            st.warning("Please ingest at least 2 tables to use this tool.")
        else:
            with st.container():
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                t1 = col1.selectbox("Select Table A", tables, key="cf_t1")
                t2 = col2.selectbox("Select Table B", tables, key="cf_t2")
                
                if t1 and t2:
                    cols1 = [c[0] for c in con.execute(f'DESCRIBE "{t1}"').fetchall()]
                    cols2 = [c[0] for c in con.execute(f'DESCRIBE "{t2}"').fetchall()]
                    
                    # Auto-detection: find exact matches
                    common_names = list(set(cols1) & set(cols2))
                    default_col = common_names[0] if common_names else cols1[0]
                    
                    st.write("---")
                    st.write("🔍 **Mapping Configuration**")
                    if common_names:
                        st.success(f"Auto-detected common column: `{default_col}`")
                    
                    mcol1, mcol2 = st.columns(2)
                    c1 = mcol1.selectbox(f"Column in {t1}", cols1, index=cols1.index(default_col) if default_col in cols1 else 0, key="cf_col1")
                    c2 = mcol2.selectbox(f"Column in {t2}", cols2, index=cols2.index(default_col) if default_col in cols2 else 0, key="cf_col2")
                    
                    if st.button("🚀 Find Common Values", type="primary", use_container_width=True):
                        query = f"""
                        SELECT count(*) as overlap_count 
                        FROM "{t1}" 
                        WHERE "{c1}" IN (SELECT "{c2}" FROM "{t2}")
                        """
                        t0 = datetime.now()
                        result = con.execute(query).df()
                        duration = (datetime.now() - t0).total_seconds()
                        
                        count = result.iloc[0, 0]
                        st.balloons()
                        
                        st.markdown(f"""
                        ### Results
                        - **Common Records Found**: `{count:,}`
                        - **Execution Time**: `{duration:.4f}s`
                        """)
                        
                        # Add to notebook option
                        if st.button("📓 Add this finding to Notebook", use_container_width=True):
                            nb_query = f"-- Common values between {t1}.{c1} and {t2}.{c2}\n"
                            nb_query += f"SELECT * FROM \"{t1}\"\nWHERE \"{c1}\" IN (SELECT \"{c2}\" FROM \"{t2}\")\nLIMIT 100;"
                            st.session_state.notebooks[st.session_state.current_notebook].append({
                                "id": datetime.now().microsecond,
                                "query": nb_query,
                                "result": None,
                                "meta": {}
                            })
                            st.session_state.active_tool = None
                            st.toast("Added to Notebook!")
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Close Tool", use_container_width=True):
                st.session_state.active_tool = None
                st.rerun()
    except Exception as e:
        st.error(f"Error in Tool: {e}")

# 2. Table Manager
elif st.session_state.managing_table:
    tn = st.session_state.managing_table
    st.markdown(f"## ⚙️ Manage Table: {tn}")
    try:
        c_info = con.execute(f'DESCRIBE "{tn}"').fetchall()
        p_data = con.execute(f'SELECT * FROM "{tn}" LIMIT 5').df()
        with st.container():
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.subheader("Preview")
            st.dataframe(p_data, use_container_width=True, hide_index=True)
            st.divider()
            
            updates = []
            for i, ci in enumerate(c_info):
                cn = ci[0]
                mc1, mc2, mc3, mc4 = st.columns([0.1, 0.4, 0.3, 0.2])
                mc1.write(f"#{i+1}")
                m_name = mc2.text_input("Name", value=cn, key=f"mname_{tn}_{cn}")
                m_keep = mc3.checkbox("Keep", value=True, key=f"mkeep_{tn}_{cn}")
                m_p = mc4.number_input("Pos", value=i, min_value=0, key=f"mpos_{tn}_{cn}")
                if m_keep: updates.append({"old": cn, "new": m_name, "pos": m_p})
            
            st.divider()
            updates.sort(key=lambda x: x["pos"])
            mc_a, mc_b = st.columns(2)
            if mc_a.button("💾 Save Changes", use_container_width=True, type="primary"):
                # 1. Rebuild table with new schema in session
                sel = ", ".join([f'"{u["old"]}" AS "{u["new"]}"' for u in updates])
                con.execute(f'CREATE TABLE "{tn}_new" AS SELECT {sel} FROM "{tn}"')
                con.execute(f'DROP TABLE "{tn}"')
                con.execute(f'ALTER TABLE "{tn}_new" RENAME TO "{tn}"')
                
                # 2. Sync to backend file storage
                os.makedirs("data", exist_ok=True)
                target_path = os.path.join("data", f"{tn}.csv")
                con.execute(f'COPY "{tn}" TO \'{target_path}\' (HEADER, DELIMITER \',\')')
                
                # 3. High-Performance Indexing (Auto-Detected)
                for u in updates:
                    col = u["new"].lower()
                    if any(key in col for key in ["id", "num", "phone", "email", "code", "key"]):
                        try:
                            con.execute(f'CREATE INDEX IF NOT EXISTS idx_{tn}_{col} ON "{tn}"("{u["new"]}")')
                        except: pass
                
                st.session_state.managing_table = None
                st.toast(f"✅ Changes & Performance Indexes persisted for: {tn}")
                st.rerun()
            if mc_b.button("Close", use_container_width=True):
                st.session_state.managing_table = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error: {e}")

# 3. Notebooks (Default)
else:
    st.markdown(f'<div class="notebook-header"><h1 style="margin:0;">📓 {st.session_state.current_notebook}</h1></div>', unsafe_allow_html=True)
    
    status_class = "status-live" if not st.session_state.read_only else "status-locked"
    status_text = "LIVE: READ-WRITE" if not st.session_state.read_only else "STANDBY: READ-ONLY"
    st.markdown(f'<div class="status-badge {status_class}">{status_text}</div>', unsafe_allow_html=True)
    
    n_col1, n_col2, n_col_s = st.columns([0.15, 0.15, 0.7])
    if n_col1.button("➕ Add Cell", key="nb_add_main", use_container_width=True):
        add_cell()
        st.rerun()
    if n_col2.button("🏃 Run All", key="nb_run_all", use_container_width=True):
        st.info("Run All triggered.")
        
    st.divider()
    st.markdown('<div class="progress-styled"></div>', unsafe_allow_html=True)
    
    # --- Autocomplete Engine (Robust Schema Detection) ---
    @st.cache_data(ttl=5)
    def get_sql_suggestions():
        try:
            # 1. Fetch all table names
            tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
            # 2. Fetch all column names across all tables
            columns = [c[0] for c in con.execute("SELECT DISTINCT column_name FROM information_schema.columns").fetchall()]
            
            # 3. Core SQL Keywords
            sql_keywords = [
                "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "LIMIT", "INSERT", "UPDATE", "DELETE",
                "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN", "ON", "AS", "DISTINCT",
                "COUNT", "SUM", "AVG", "MIN", "MAX", "HAVING", "IN", "BETWEEN", "LIKE", "IS NULL", "IS NOT NULL",
                "AND", "OR", "CASE", "WHEN", "THEN", "ELSE", "END", "CAST", "COALESCE", "WINDOW", "OVER", "PARTITION BY"
            ]
            
            # 4. Custom Macros
            macros = ["@top_users", "@daily_agg"]
            
            # Combine, deduplicate, and sort
            suggestions = list(set(tables + columns + sql_keywords + macros))
            return sorted(suggestions)
        except: 
            return ["SELECT", "FROM", "WHERE", "LIMIT"]

    suggestions = get_sql_suggestions()
    
    active_cells = get_active_cells()
    for i, cell in enumerate(active_cells):
        with st.container():
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="cell-index">[{i+1}]</div>', unsafe_allow_html=True)
            
            # Enhanced ACE Editor for high-performance SQL editing
            c_query = st_ace(
                value=cell["query"],
                placeholder="Write your SQL here (e.g. SELECT * FROM sales)...",
                language="sql",
                theme="monokai",
                font_size=15,
                tab_size=4,
                show_gutter=True,
                show_print_margin=False,
                wrap=True,
                auto_update=False,
                key=f"ace_{st.session_state.current_notebook}_{cell['id']}"
            )
            
            st.write("")
            acol1, acol2, acol3 = st.columns([0.15, 0.15, 0.7])
            r_now = acol1.button("▶ RUN", key=f"run_btn_{st.session_state.current_notebook}_{cell['id']}", type="primary", use_container_width=True)
            d_now = acol2.button("🗑️", key=f"del_btn_{st.session_state.current_notebook}_{cell['id']}", use_container_width=True)
            
            if d_now: delete_cell(i)
            
            active_cells[i]["query"] = c_query
            do_run = r_now or (c_query != cell.get("last_run_query") and c_query.strip() != "")
            
            if do_run:
                from macros import expand_macros
                try:
                    p_query = expand_macros(c_query)
                    t0 = datetime.now()
                    res_df = con.execute(p_query).df()
                    dur = (datetime.now() - t0).total_seconds()
                    active_cells[i].update({"result": res_df, "error": None, "last_run_query": c_query, "meta": {"time": dur, "rows": len(res_df)}})
                except Exception as ex:
                    er = str(ex)
                    lm = re.search(r"at line (\d+)", er)
                    cm = re.search(r"column (\d+)", er)
                    active_cells[i].update({"result": "ERROR", "last_run_query": c_query, "error": {"msg": er, "line": lm.group(1) if lm else None, "col": cm.group(1) if cm else None}})

            if active_cells[i]["result"] is not None:
                res = active_cells[i]["result"]
                if isinstance(res, pd.DataFrame):
                    meta = active_cells[i]["meta"]
                    st.divider()
                    st.caption(f"✨ Executed in {meta['time']:.4f}s • {meta['rows']} rows")
                    st.dataframe(res, use_container_width=True, hide_index=True)
                elif res == "ERROR":
                    e_obj = active_cells[i].get("error", {})
                    st.divider()
                    st.error(f"❌ Execution Error\n\n{e_obj.get('msg')}")
                    if e_obj.get("line"): st.info(f"📍 Line {e_obj['line']}, Column {e_obj['col']}")
            
            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    with st.expander("💡 Power User Tips"):
        st.markdown("- Press **Cmd + Enter** to run high-speed SQL queries.\n- Use **@macros** for complex aggregate snippets.")
