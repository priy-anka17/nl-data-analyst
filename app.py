"""Natural Language Data Analyst — Streamlit UI."""

import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NL Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .main-header {
        background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 50%, #8b5cf6 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.2);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
        font-family: 'Inter', sans-serif;
    }
    .main-header p {
        color: #c4b5fd;
        font-size: 1.15rem;
        margin: 0.5rem 0 0;
    }
    .step-card {
        background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(168,85,247,0.08) 100%);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 12px;
        padding: 1.4rem 1rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .step-card:hover { transform: translateY(-2px); border-color: rgba(139,92,246,0.5); }
    .step-card h3 { color: #a78bfa; margin: 0 0 0.4rem; font-size: 1.05rem; }
    .step-card p  { color: #94a3b8; margin: 0; font-size: 0.88rem; }
    .step-num {
        display: inline-block;
        background: #8b5cf6;
        color: #1e1b4b;
        width: 28px; height: 28px;
        border-radius: 50%;
        font-weight: 700;
        line-height: 28px;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
    }
    .stat-card {
        background: rgba(139,92,246,0.08);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stat-card .value { font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
    .stat-card .label { font-size: 0.82rem; color: #94a3b8; margin-top: 2px; }
    .tech-badge {
        display: inline-block;
        background: rgba(139,92,246,0.12);
        border: 1px solid rgba(139,92,246,0.3);
        color: #a78bfa;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        margin: 3px;
        font-weight: 500;
    }
    .code-block {
        background: #1e1b4b;
        border: 1px solid rgba(139,92,246,0.3);
        border-radius: 8px;
        padding: 1rem;
        overflow-x: auto;
    }
    div[data-testid="stChatMessage"] {
        border: 1px solid rgba(139,92,246,0.1);
        border-radius: 12px;
    }
</style>""",
    unsafe_allow_html=True,
)

# ── Session state ────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "analyzer" not in st.session_state:
    st.session_state.analyzer = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "data_name" not in st.session_state:
    st.session_state.data_name = ""

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        help="Get a free key at https://console.groq.com/keys",
    )
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    st.divider()

    # File upload
    st.markdown("### 📁 Upload Data")
    uploaded = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls"],
        help="Max 50 MB",
    )

    if uploaded:
        try:
            if uploaded.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(uploaded)
            else:
                df = pd.read_csv(uploaded)
            st.session_state.df = df
            st.session_state.data_name = uploaded.name
            from engine.analyzer import DataAnalyzer
            st.session_state.analyzer = DataAnalyzer(df)
            st.success(f"Loaded **{uploaded.name}** ({df.shape[0]:,} rows × {df.shape[1]} cols)")
        except Exception as e:
            st.error(f"Error loading file: {e}")

    st.divider()

    # Sample datasets
    st.markdown("### 📋 Sample Datasets")
    sample_options = {
        "None": None,
        "🛒 E-Commerce Sales": "data/sample/ecommerce_sales.csv",
        "👥 Employee HR Data": "data/sample/employee_hr.csv",
        "🌡️ Weather Records": "data/sample/weather_data.csv",
    }
    selected_sample = st.selectbox("Try a sample dataset", list(sample_options.keys()))
    if selected_sample != "None" and sample_options[selected_sample]:
        sample_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            sample_options[selected_sample],
        )
        if os.path.exists(sample_path):
            if st.button("Load Sample", use_container_width=True):
                df = pd.read_csv(sample_path)
                st.session_state.df = df
                st.session_state.data_name = selected_sample.split(" ", 1)[1]
                from engine.analyzer import DataAnalyzer
                st.session_state.analyzer = DataAnalyzer(df)
                st.session_state.chat_history = []
                st.rerun()

    st.divider()

    tech_badges = ["Groq / Llama 3.1", "Pandas", "Plotly", "LangChain", "Streamlit"]
    st.markdown(
        " ".join(f'<span class="tech-badge">{t}</span>' for t in tech_badges),
        unsafe_allow_html=True,
    )

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    if st.button("🔄 Reset Data", use_container_width=True):
        st.session_state.df = None
        st.session_state.analyzer = None
        st.session_state.chat_history = []
        st.session_state.data_name = ""
        st.rerun()

# ── Helper ───────────────────────────────────────────────────────────────────

def _build_suggestions(df: pd.DataFrame) -> list[str]:
    """Build smart question suggestions based on the DataFrame."""
    suggestions = []
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    if num_cols:
        suggestions.append(f"What is the average {num_cols[0]}?")
    if len(num_cols) >= 2:
        suggestions.append(f"Show a scatter plot of {num_cols[0]} vs {num_cols[1]}")
    if cat_cols and num_cols:
        suggestions.append(f"What is the average {num_cols[0]} by {cat_cols[0]}?")
    if cat_cols:
        suggestions.append(f"What are the top 10 most common {cat_cols[0]}?")
    if date_cols and num_cols:
        suggestions.append(f"Show the trend of {num_cols[0]} over {date_cols[0]}")
    if not suggestions:
        suggestions = ["Summarize this dataset", "Show missing values by column"]

    suggestions.append("Give me a full summary of this dataset")

    cols = st.columns(min(len(suggestions), 3))
    for i, s in enumerate(suggestions[:6]):
        if cols[i % 3].button(f"💡 {s}", key=f"sug_{i}", use_container_width=True):
            st.session_state["_pending_question"] = s
            st.rerun()

    st.session_state["suggestions"] = suggestions
    st.session_state["suggestions_built"] = True
    return suggestions


# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="main-header">
    <h1>📊 Natural Language Data Analyst</h1>
    <p>Upload data. Ask questions in plain English. Get instant analysis & charts.</p>
</div>""",
    unsafe_allow_html=True,
)

# ── How it works cards ───────────────────────────────────────────────────────
steps = [
    ("1", "📁 Upload", "CSV or Excel file — any dataset"),
    ("2", "💬 Ask", "Questions in plain English about your data"),
    ("3", "🐍 Generate", "AI writes pandas code to answer your question"),
    ("4", "📊 Visualize", "Get results, tables, and interactive charts"),
]
cols = st.columns(4)
for col, (num, title, desc) in zip(cols, steps):
    col.markdown(
        f'<div class="step-card">'
        f'<div class="step-num">{num}</div>'
        f"<h3>{title}</h3><p>{desc}</p></div>",
        unsafe_allow_html=True,
    )

st.markdown("")

# ── Data preview ─────────────────────────────────────────────────────────────
df = st.session_state.df

if df is not None:
    st.markdown(f"### 📋 Data Preview — {st.session_state.data_name}")

    # Stats row
    num_cols = len(df.select_dtypes(include="number").columns)
    cat_cols = len(df.select_dtypes(exclude="number").columns)
    missing = int(df.isnull().sum().sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    for col_el, val, label in [
        (c1, f"{df.shape[0]:,}", "Rows"),
        (c2, str(df.shape[1]), "Columns"),
        (c3, str(num_cols), "Numeric"),
        (c4, str(cat_cols), "Categorical"),
        (c5, f"{missing:,}", "Missing Values"),
    ]:
        col_el.markdown(
            f'<div class="stat-card"><div class="value">{val}</div>'
            f'<div class="label">{label}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    with st.expander("🔍 View Data Sample", expanded=False):
        st.dataframe(df.head(20), use_container_width=True)

    with st.expander("📈 Column Types & Stats", expanded=False):
        col_info = pd.DataFrame(
            {
                "Type": df.dtypes.astype(str),
                "Non-Null": df.count(),
                "Null": df.isnull().sum(),
                "Unique": df.nunique(),
            }
        )
        st.dataframe(col_info, use_container_width=True)

    st.markdown("---")

    # ── Suggested questions ──────────────────────────────────────────────
    st.markdown("### 💡 Suggested Questions")
    _build_suggestions(df)

    # Handle pending suggestion click
    pending = st.session_state.pop("_pending_question", None)

    # ── Chat interface ───────────────────────────────────────────────────
    st.markdown("### 💬 Ask Your Data")

    # Display chat history
    for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(entry["question"])
        with st.chat_message("assistant", avatar="📊"):
            if entry["success"]:
                st.markdown(entry["output"])
                if entry.get("chart_spec"):
                    try:
                        fig = go.Figure(entry["chart_spec"])
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
                with st.expander("🐍 View Generated Code"):
                    st.code(entry["code"], language="python")
                if entry["retries"] > 0:
                    st.caption(f"Self-corrected {entry['retries']} time(s)")
            else:
                st.error(f"Analysis failed: {entry['error']}")
                with st.expander("🐍 View Generated Code"):
                    st.code(entry["code"], language="python")

    # Chat input
    question = st.chat_input("Ask anything about your data...")

    # Use pending suggestion if no direct input
    if not question and pending:
        question = pending

    if question:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant", avatar="📊"):
            analyzer = st.session_state.analyzer
            with st.spinner("Analyzing your data..."):
                result = analyzer.ask(question)

            if result.success:
                st.markdown(result.output)
                if result.chart_spec:
                    try:
                        fig = go.Figure(result.chart_spec)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
                with st.expander("🐍 View Generated Code"):
                    st.code(result.code, language="python")
                if result.retries > 0:
                    st.caption(f"Self-corrected {result.retries} time(s)")
            else:
                st.error(f"Analysis failed after {result.retries} retries")
                with st.expander("🐍 View Code & Error"):
                    st.code(result.code, language="python")
                    st.text(result.error)

        st.session_state.chat_history.append(
            {
                "question": result.question,
                "code": result.code,
                "output": result.output,
                "chart_spec": result.chart_spec,
                "error": result.error,
                "retries": result.retries,
                "success": result.success,
            }
        )

else:
    if not api_key:
        st.info("👈 Enter your **Groq API key** in the sidebar to get started. [Get a free key →](https://console.groq.com/keys)")
    else:
        st.info("👈 **Upload a CSV/Excel file** or **load a sample dataset** from the sidebar to start analyzing.")


