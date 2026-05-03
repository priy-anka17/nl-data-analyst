# 📊 Natural Language Data Analyst

> Upload any dataset. Ask questions in plain English. Get instant analysis, visualizations, and generated code.

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge)](https://nl-data-analyst.streamlit.app)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

### [▶️ Try the Live Demo](https://nl-data-analyst.streamlit.app)

## The Problem

Data analysis requires knowing pandas, SQL, or specialized tools. Business users have questions about their data but can't write code to get answers. Even experienced analysts spend time writing repetitive groupby/pivot/visualization code.

## The Solution

This system lets you **ask questions about any dataset in plain English**. An AI agent:
1. Reads your dataset schema
2. Generates pandas code to answer your question
3. Executes the code safely
4. Returns results, tables, and interactive Plotly charts
5. **Self-corrects** if the code fails (up to 2 retries)

```
                    ┌─────────────────────────────────────┐
                    │      "What's the average salary      │
                    │       by department?"                 │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │       1. SCHEMA ANALYSIS             │
                    │    Reads columns, types, stats       │
                    │    from your uploaded data            │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │       2. CODE GENERATION             │
                    │    LLM writes pandas + plotly        │
                    │    code to answer the question        │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │       3. SAFE EXECUTION              │
                    │    Runs code in sandboxed env        │
                    │    with error handling                │
                    └──────────────┬──────────────────────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                       ✅ Success        ❌ Error
                          │                 │
                  Show results +      Auto-fix code
                  charts to user      & retry (2x)
```

## Key Features

- **Natural Language Queries** — Ask anything: aggregations, comparisons, trends, distributions
- **Auto Chart Generation** — AI creates Plotly charts when visualization helps
- **Self-Correcting Code** — If generated code fails, the LLM auto-fixes and retries
- **Code Transparency** — See the exact pandas code generated for every answer
- **Multi-Format Support** — Upload CSV or Excel files (up to 50 MB)
- **Smart Suggestions** — Auto-generated question suggestions based on your data
- **Chat History** — Full conversation with your data, like ChatGPT for spreadsheets
- **Sample Datasets** — 3 built-in datasets to try instantly
- **Zero Setup** — No database, no schema configuration, just upload and ask

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq (Llama 3.1 8B) — free, fast inference |
| Code Gen | LangChain with structured prompts |
| Data Processing | Pandas |
| Visualization | Plotly (interactive charts) |
| UI | Streamlit |

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/priy-anka17/nl-data-analyst.git
cd nl-data-analyst
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your Groq API key (or enter it in the sidebar)
```

### 3. Run

```bash
streamlit run app.py
```

### 4. Try It

1. Load a **sample dataset** from the sidebar (e.g., E-Commerce Sales)
2. Ask: *"What are the top 5 categories by total revenue?"*
3. Ask: *"Show a bar chart of sales by region"*
4. Or upload your own CSV/Excel!

## Sample Questions

**E-Commerce Sales:**
- "What's the total revenue by category?"
- "Show monthly sales trend as a line chart"
- "Which region has the highest average order value?"
- "What's the distribution of customer ages?"

**Employee HR Data:**
- "What's the average salary by department and level?"
- "Show a box plot of salaries by department"
- "How many remote vs office employees per department?"
- "What's the correlation between experience and performance?"

**Weather Data:**
- "What's the average temperature by city?"
- "Show temperature trends over months for all cities"
- "Which city has the most rainy days?"

## Project Structure

```
nl-data-analyst/
├── app.py                     # Streamlit UI with chat interface
├── config.py                  # Configuration & environment variables
├── requirements.txt           # Python dependencies
├── runtime.txt                # Python 3.11 for Streamlit Cloud
├── .env.example               # Environment template
├── engine/
│   └── analyzer.py            # Core: NL → pandas code → execution
└── data/
    └── sample/                # Sample datasets (CSV)
        ├── ecommerce_sales.csv
        ├── employee_hr.csv
        └── weather_data.csv
```

## How It Works

1. **Schema Extraction** — When you upload data, the engine extracts column names, types, statistics, and sample rows
2. **Prompt Engineering** — Your question + schema is sent to the LLM with strict rules (use `df`, store result in `result`, optionally create `fig` for charts)
3. **Code Generation** — The LLM returns pure pandas/plotly code
4. **Safe Execution** — Code runs in a controlled namespace with pandas and plotly pre-imported
5. **Self-Correction** — If execution fails, the error is sent back to the LLM to fix the code (up to 2 retries)
6. **Display** — Results are shown as text/tables + interactive Plotly charts

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | llama-3.1-8b-instant | Groq model for code generation |
| `MAX_RETRIES` | 2 | Auto-fix attempts on code errors |

## 🚀 Live Demo

**[Try it live on Streamlit Cloud →](https://nl-data-analyst.streamlit.app)**

No installation needed — just enter your free [Groq API key](https://console.groq.com/keys) and upload any dataset.

## Deploy Your Own

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your fork, set main file to `app.py`, click **Deploy**

## License

MIT

---

Built with ❤️ using LangChain, Pandas, Plotly, and Streamlit
