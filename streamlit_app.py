"""Interactive Streamlit viewer for the three Krall--Sheffer constructions."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from sympy import expand, factor, latex, simplify

from most_intriguing import Q_hyper, Q_operational, Q_rodrigues


APP_TITLE = "Krall–Sheffer Most Intriguing Case"
MAX_DEGREE = 8


def _validate_style(style: str) -> str:
    normalized = style.lower()
    if normalized not in {"expanded", "factored"}:
        raise ValueError("style must be 'expanded' or 'factored'")
    return normalized


def _styled_expression(expr: Any, style: str):
    """Return an expression in the selected display style."""
    return factor(expr) if _validate_style(style) == "factored" else expand(expr)


@st.cache_data(show_spinner=False)
def polynomial_to_latex(expr: Any, style: str) -> str:
    """Format a SymPy polynomial as LaTeX in the selected style."""
    return latex(_styled_expression(expr, style))


@st.cache_data(show_spinner=False)
def polynomial_to_text(expr: Any, style: str) -> str:
    """Format a SymPy polynomial as plain text in the selected style."""
    styled = _styled_expression(expr, style)
    return str(styled if style.lower() == "factored" else expand(styled))


@st.cache_data(show_spinner="Computing the three symbolic constructions…")
def compute_three_constructions(n: int, style: str) -> list[dict[str, Any]]:
    """Compute all three constructions and their exact differences for Q_n."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    _validate_style(style)

    rows: list[dict[str, Any]] = []
    for k in range(n + 1):
        rod = Q_rodrigues(n, k)
        op = Q_operational(n, k)
        hyp = Q_hyper(n, k)
        rows.append(
            {
                "k": k,
                "rod": _styled_expression(rod, style),
                "op": _styled_expression(op, style),
                "hyp": _styled_expression(hyp, style),
                "diff_rod_op": simplify(expand(rod - op)),
                "diff_op_hyp": simplify(expand(op - hyp)),
            }
        )
    return rows


def build_latex_export(n: int, rows: list[dict[str, Any]], style: str) -> str:
    """Build readable LaTeX display blocks for a complete polynomial vector."""
    blocks = [f"% Krall--Sheffer three constructions for degree n={n}"]
    for row in rows:
        k = row["k"]
        blocks.extend(
            [
                r"\[",
                rf"Q_{{{n},{k}}}^{{\mathrm{{Rod}}}} = {polynomial_to_latex(row['rod'], style)}",
                r"\]",
                "",
                r"\[",
                rf"Q_{{{n},{k}}}^{{\mathrm{{op}}}} = {polynomial_to_latex(row['op'], style)}",
                r"\]",
                "",
                r"\[",
                rf"Q_{{{n},{k}}}^{{\mathrm{{hyp}}}} = {polynomial_to_latex(row['hyp'], style)}",
                r"\]",
                "",
                r"\[",
                (
                    rf"Q_{{{n},{k}}}^{{\mathrm{{Rod}}}}-Q_{{{n},{k}}}^{{\mathrm{{op}}}}"
                    rf" = {latex(row['diff_rod_op'])},\qquad"
                ),
                (
                    rf"Q_{{{n},{k}}}^{{\mathrm{{op}}}}-Q_{{{n},{k}}}^{{\mathrm{{hyp}}}}"
                    rf" = {latex(row['diff_op_hyp'])}."
                ),
                r"\]",
                "",
            ]
        )
    return "\n".join(blocks)


def build_markdown_export(n: int, rows: list[dict[str, Any]], style: str) -> str:
    """Build a Markdown document containing readable math blocks."""
    lines = [f"# Krall–Sheffer polynomials of degree {n}", ""]
    for row in rows:
        k = row["k"]
        lines.extend(
            [
                f"## $Q_{{{n},{k}}}$",
                "",
                rf"$$Q_{{{n},{k}}}^{{\mathrm{{Rod}}}} = {polynomial_to_latex(row['rod'], style)}$$",
                "",
                rf"$$Q_{{{n},{k}}}^{{\mathrm{{op}}}} = {polynomial_to_latex(row['op'], style)}$$",
                "",
                rf"$$Q_{{{n},{k}}}^{{\mathrm{{hyp}}}} = {polynomial_to_latex(row['hyp'], style)}$$",
                "",
                (
                    rf"$$Q_{{{n},{k}}}^{{\mathrm{{Rod}}}}-Q_{{{n},{k}}}^{{\mathrm{{op}}}}"
                    rf" = {latex(row['diff_rod_op'])},\qquad "
                    rf"Q_{{{n},{k}}}^{{\mathrm{{op}}}}-Q_{{{n},{k}}}^{{\mathrm{{hyp}}}}"
                    rf" = {latex(row['diff_op_hyp'])}.$$"
                ),
                "",
            ]
        )
    return "\n".join(lines)


def build_text_export(n: int, rows: list[dict[str, Any]], style: str) -> str:
    """Build a plain-text representation of all constructions."""
    lines = [f"Krall-Sheffer three constructions for degree n={n}", ""]
    for row in rows:
        k = row["k"]
        lines.extend(
            [
                f"Q_{{{n},{k}}}^{{Rod}} = {polynomial_to_text(row['rod'], style)}",
                f"Q_{{{n},{k}}}^{{op}} = {polynomial_to_text(row['op'], style)}",
                f"Q_{{{n},{k}}}^{{hyp}} = {polynomial_to_text(row['hyp'], style)}",
                f"Rod - op = {row['diff_rod_op']}",
                f"op - hyp = {row['diff_op_hyp']}",
                "",
            ]
        )
    return "\n".join(lines)


def _show_vector(rows: list[dict[str, Any]], key: str, label: str, n: int, style: str) -> None:
    st.subheader(f"{label}: $Q_{n}$")
    for row in rows:
        st.markdown(rf"**$Q_{{{n},{row['k']}}}^{{\mathrm{{{label}}}}}$**")
        st.latex(polynomial_to_latex(row[key], style))


def _render_side_by_side(n: int, rows: list[dict[str, Any]], style: str) -> None:
    for row in rows:
        k = row["k"]
        st.header(rf"$Q_{{{n},{k}}}$")
        columns = st.columns(3)
        for column, heading, key in zip(
            columns,
            ("Rodrigues", "Operational", "Hypergeometric/Horn"),
            ("rod", "op", "hyp"),
            strict=True,
        ):
            with column:
                st.markdown(f"**{heading}**")
                st.latex(polynomial_to_latex(row[key], style))

        first = row["diff_rod_op"]
        second = row["diff_op_hyp"]
        message = f"Rod - op = {first}    |    op - hyp = {second}"
        if first == 0 and second == 0:
            st.success(message)
        else:
            st.error(message)


def _render_tabs(
    n: int,
    rows: list[dict[str, Any]],
    style: str,
    latex_export: str,
    markdown_export: str,
    text_export: str,
) -> None:
    rod_tab, op_tab, hyp_tab, differences_tab, raw_tab = st.tabs(
        ["Rodrigues", "Operational", "Hypergeometric", "Differences", "Raw text / export"]
    )
    with rod_tab:
        _show_vector(rows, "rod", "Rod", n, style)
    with op_tab:
        _show_vector(rows, "op", "op", n, style)
    with hyp_tab:
        _show_vector(rows, "hyp", "hyp", n, style)
    with differences_tab:
        for row in rows:
            k = row["k"]
            st.markdown(rf"**$Q_{{{n},{k}}}$**")
            st.latex(
                rf"Q_{{{n},{k}}}^{{\mathrm{{Rod}}}}-Q_{{{n},{k}}}^{{\mathrm{{op}}}}"
                rf" = {latex(row['diff_rod_op'])}"
            )
            st.latex(
                rf"Q_{{{n},{k}}}^{{\mathrm{{op}}}}-Q_{{{n},{k}}}^{{\mathrm{{hyp}}}}"
                rf" = {latex(row['diff_op_hyp'])}"
            )
    with raw_tab:
        st.code(text_export, language="text")
        _render_downloads(n, latex_export, markdown_export, text_export, key_prefix="tabs")


def _render_comparison_table(n: int, rows: list[dict[str, Any]], style: str) -> None:
    table_rows = [
        {
            "k": row["k"],
            "Q^{Rod}": polynomial_to_text(row["rod"], style),
            "Q^{op}": polynomial_to_text(row["op"], style),
            "Q^{hyp}": polynomial_to_text(row["hyp"], style),
            "Rod - op": str(row["diff_rod_op"]),
            "op - hyp": str(row["diff_op_hyp"]),
        }
        for row in rows
    ]
    st.subheader(rf"Comparison table for $Q_{n}$")
    st.dataframe(pd.DataFrame(table_rows), hide_index=True, use_container_width=True)


def _render_downloads(
    n: int,
    latex_export: str,
    markdown_export: str,
    text_export: str,
    key_prefix: str = "main",
) -> None:
    st.subheader("Downloads")
    columns = st.columns(3)
    columns[0].download_button(
        "Download LaTeX blocks",
        latex_export,
        file_name=f"Q_{n}_three_constructions.tex",
        mime="application/x-tex",
        key=f"{key_prefix}-latex",
        use_container_width=True,
    )
    columns[1].download_button(
        "Download Markdown",
        markdown_export,
        file_name=f"Q_{n}_three_constructions.md",
        mime="text/markdown",
        key=f"{key_prefix}-markdown",
        use_container_width=True,
    )
    columns[2].download_button(
        "Download plain text",
        text_export,
        file_name=f"Q_{n}_three_constructions.txt",
        mime="text/plain",
        key=f"{key_prefix}-text",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="∂", layout="wide")
    st.title(APP_TITLE)

    with st.sidebar:
        st.header("Display controls")
        n = int(st.number_input("Degree n", min_value=0, max_value=MAX_DEGREE, value=3, step=1))
        style = st.radio("Output style", ["expanded", "factored"], horizontal=True)
        display_mode = st.selectbox("Display mode", ["Side-by-side", "Tabs", "Comparison table"])
        st.caption(f"Maximum supported interactive degree: n = {MAX_DEGREE}.")
        if n >= 7:
            st.warning("High degrees can take longer because all three symbolic constructions are computed exactly.")

    st.markdown(r"$Q_{n,k}(x,y)$ corresponds to $x^{n-k}y^k$, with $0\leq k\leq n$.")
    st.markdown("**Operational construction**")
    st.latex(r"R = 3y\partial_x^2 + \partial_x\partial_y - \frac{1}{2}\partial_x^3")
    st.latex(
        r"Q_{n,k}^{\mathrm{op}} = (-1)^n \exp(-R)"
        r"\left[\binom{n}{k}x^{n-k}y^k\right]"
    )
    st.markdown("**Krall–Sheffer differential operator**")
    st.latex(r"L = 3y\partial_x^2 + 2\partial_x\partial_y - x\partial_x - y\partial_y")
    st.divider()

    rows = compute_three_constructions(n, style)
    latex_export = build_latex_export(n, rows, style)
    markdown_export = build_markdown_export(n, rows, style)
    text_export = build_text_export(n, rows, style)

    if display_mode == "Side-by-side":
        _render_side_by_side(n, rows, style)
    elif display_mode == "Tabs":
        _render_tabs(n, rows, style, latex_export, markdown_export, text_export)
    else:
        _render_comparison_table(n, rows, style)

    if display_mode != "Tabs":
        st.divider()
        _render_downloads(n, latex_export, markdown_export, text_export)


if __name__ == "__main__":
    main()
