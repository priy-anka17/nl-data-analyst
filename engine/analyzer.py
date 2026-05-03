"""Core analysis engine — generates & executes pandas code from natural language."""

from __future__ import annotations

import io
import re
import traceback
from dataclasses import dataclass, field

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import GROQ_BASE_URL, LLM_MODEL, MAX_RETRIES, get_groq_api_key


@dataclass
class AnalysisResult:
    """Result of a natural language analysis."""

    question: str
    code: str
    output: str
    chart_spec: dict | None = None
    error: str = ""
    retries: int = 0
    success: bool = True


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=get_groq_api_key(),
        base_url=GROQ_BASE_URL,
        model=LLM_MODEL,
        temperature=0,
    )


def _get_dataframe_schema(df: pd.DataFrame) -> str:
    """Build a concise schema description of a DataFrame."""
    buf = io.StringIO()
    df.info(buf=buf)
    info_str = buf.getvalue()

    sample = df.head(3).to_string(max_cols=20)
    stats_cols = df.select_dtypes(include="number").columns.tolist()[:10]
    stats = df[stats_cols].describe().to_string() if stats_cols else "No numeric columns"

    return (
        f"=== DataFrame Info ===\n{info_str}\n\n"
        f"=== Sample Rows (first 3) ===\n{sample}\n\n"
        f"=== Numeric Statistics ===\n{stats}\n\n"
        f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
        f"Columns: {list(df.columns)}\n"
        f"Dtypes: {dict(df.dtypes.astype(str))}"
    )


SYSTEM_PROMPT = """\
You are an expert data analyst. You have a pandas DataFrame called `df` already loaded in memory.

SCHEMA:
{schema}

Given the user's question, write Python code using pandas to answer it.

RULES:
1. The DataFrame is already loaded as `df`. Do NOT read from any file.
2. Store your final answer in a variable called `result`.
   - For single numbers: round to 2 decimal places and format as a readable string, e.g. result = f"The average salary is **${avg:,.2f}**"
   - For DataFrames: limit to top 10-20 rows max. Use .head(10) or .nlargest()/.nsmallest() as appropriate.
   - For summaries: build a well-formatted multi-line string with bullet points and sections.
   - ALWAYS make `result` a human-readable formatted string when the answer is a single value.
3. If a chart would help, create a Plotly figure and store it in a variable called `fig`. Use plotly.express or plotly.graph_objects. Apply a clean style with title, axis labels, and color.
4. Always handle potential errors (missing columns, NaN values) gracefully.
5. Do NOT use print(). Just assign to `result`.
6. Do NOT import pandas — it's already imported as `pd`.
7. Do NOT modify the original `df`. Use copies if needed.
8. Return ONLY the Python code inside a ```python code block. No explanations outside the code block.
9. Keep code concise — ideally under 30 lines.
10. For groupby/aggregations, reset_index() so result is a clean DataFrame. Sort by the aggregated column descending.
11. When grouping by a column, NEVER group by unique ID columns (like employee_id, order_id, etc). Use meaningful categorical columns (department, category, region, etc).
12. ALWAYS create a `fig` chart when the result is a DataFrame with aggregated data — use bar charts, pie charts, or line charts as appropriate.
"""

FIX_PROMPT = """\
The previous code produced an error. Fix it.

Previous code:
```python
{code}
```

Error:
{error}

Write corrected code following the same rules. Return ONLY the Python code inside a ```python code block.
"""


def _extract_code(text: str) -> str:
    """Extract Python code from LLM response."""
    # Look for ```python ... ``` blocks
    match = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: look for any ``` block
    match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Last resort: assume the whole response is code
    return text.strip()


def _execute_code(code: str, df: pd.DataFrame) -> tuple[str, dict | None, str]:
    """Execute generated code safely and return (output, chart_spec, error)."""
    import plotly.express as px  # noqa: F401
    import plotly.graph_objects as go  # noqa: F401

    local_vars: dict = {"df": df.copy(), "pd": pd, "px": px, "go": go}

    try:
        exec(code, {"__builtins__": __builtins__}, local_vars)  # noqa: S102
    except Exception:
        return "", None, traceback.format_exc()

    # Extract result
    result = local_vars.get("result", None)
    fig = local_vars.get("fig", None)

    # Format output
    if result is None:
        output = "Code executed but no `result` variable was set."
    elif isinstance(result, pd.DataFrame):
        # Limit rows and render as markdown table
        display_df = result.head(20).copy()
        # Round numeric columns for readability
        for col in display_df.select_dtypes(include="number").columns:
            display_df[col] = display_df[col].apply(
                lambda x: round(x, 2) if pd.notna(x) else x
            )
        output = display_df.to_markdown(index=False)
    elif isinstance(result, pd.Series):
        output = result.round(2).to_markdown()
    else:
        output = str(result)

    # Extract chart
    chart_spec = None
    if fig is not None:
        try:
            chart_spec = fig.to_dict()
        except Exception:
            pass

    return output, chart_spec, ""


class DataAnalyzer:
    """Orchestrates NL question → code generation → execution → result."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.schema = _get_dataframe_schema(df)

    def ask(self, question: str) -> AnalysisResult:
        """Answer a natural language question about the data."""
        llm = _get_llm()

        # Generate code
        resp = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT.format(schema=self.schema)),
                HumanMessage(content=question),
            ]
        )
        code = _extract_code(resp.content)

        # Execute with retry loop
        retries = 0
        while True:
            output, chart_spec, error = _execute_code(code, self.df)

            if not error:
                return AnalysisResult(
                    question=question,
                    code=code,
                    output=output,
                    chart_spec=chart_spec,
                    retries=retries,
                )

            retries += 1
            if retries > MAX_RETRIES:
                return AnalysisResult(
                    question=question,
                    code=code,
                    output="",
                    error=error,
                    retries=retries,
                    success=False,
                )

            # Ask LLM to fix
            resp = llm.invoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT.format(schema=self.schema)),
                    HumanMessage(
                        content=FIX_PROMPT.format(code=code, error=error)
                    ),
                ]
            )
            code = _extract_code(resp.content)

    def summarize(self) -> AnalysisResult:
        """Generate an automatic summary of the dataset."""
        return self.ask(
            "Give me a comprehensive summary of this dataset. Include: "
            "total rows/columns, data types, missing values count per column, "
            "key statistics for numeric columns, and unique value counts for "
            "categorical columns (top 5 categories each). "
            "Format result as a readable string."
        )
