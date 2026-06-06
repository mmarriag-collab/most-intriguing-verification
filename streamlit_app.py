"""Interactive Streamlit viewer for the three Krall--Sheffer constructions."""

from __future__ import annotations

from typing import Any

import streamlit as st
import sympy as sp
from sympy import expand, latex, simplify

from most_intriguing import Phi_second_kind, Q_hyper, Q_operational, Q_rodrigues


APP_TITLE = "Krall–Sheffer Most Intriguing Case"
MAX_DEGREE = 8

PHI_AND_WEIGHT_LATEX = (
    r"\Phi=\begin{pmatrix}3y&1\\1&0\end{pmatrix},"
    r"\quad \omega(x,y)=e^{y^3-xy}."
)
L_OPERATOR_LATEX = (
    r"L=3y\partial_x^2+2\partial_x\partial_y-x\partial_x-y\partial_y."
)
INDEXING_LATEX = (
    r"Q_{n,k}\quad\text{corresponds to}\quad x^{n-k}y^k,"
    r"\quad 0\leq k\leq n."
)
RODRIGUES_VECTOR_LATEX = (
    r"\mathbf Q_n^{\mathrm{Rod}}(x,y)^t="
    r"\frac{1}{\omega}\operatorname{div}^{n}\left(\Phi^{n}\omega\right)."
)
RODRIGUES_COMPONENT_LATEX = (
    r"Q_{n,k}^{\mathrm{Rod}}="
    r"\sum_{i=0}^n\binom{n}{i}"
    r"(D_x^\omega)^{n-i}(D_y^\omega)^i"
    r"\left((\Phi^{n})_{i,k}\right)."
)
GAUGE_DERIVATIVES_LATEX = (
    r"D_x^\omega(p)=\partial_xp-yp,\quad"
    r"D_y^\omega(p)=\partial_yp+(3y^2-x)p."
)
GAUGE_IDENTITY_LATEX = (
    r"\frac{1}{\omega}\partial_x(p\omega)=D_x^\omega(p),\quad"
    r"\frac{1}{\omega}\partial_y(p\omega)=D_y^\omega(p)."
)
KRONECKER_VARIABLES_LATEX = r"z_1=3yt_1+t_2,\quad z_2=t_1."
KRONECKER_DEFINITION_LATEX = (
    r"(\Phi^{n})_{i,j}=[t_1^{n-j}t_2^j]\,z_1^{n-i}z_2^i."
)
R_OPERATOR_LATEX = (
    r"\mathcal R=3y\partial_x^2+\partial_x\partial_y-\frac12\partial_x^3."
)
OPERATIONAL_FORMULA_LATEX = (
    r"Q_{n,k}^{\mathrm{op}}(x,y)=(-1)^n e^{-\mathcal R}"
    r"\left[\binom{n}{k}x^{n-k}y^k\right]."
)
EXPONENTIAL_SERIES_LATEX = (
    r"e^{-\mathcal R}p=\sum_{m\geq0}\frac{(-1)^m}{m!}\mathcal R^m p."
)
HYPER_FORMULA_LATEX = (
    r"Q_{n,k}^{\mathrm{hyp}}(x,y)=n!"
    r"\sum_{\substack{i,j,\ell\geq0\\2i+j+3\ell\leq n-k\\j\leq k}}"
    r"\frac{(-x)^{n-k-2i-j-3\ell}(-y)^{k-j}(-3y)^i(-1)^j(-2)^\ell}"
    r"{(n-k-2i-j-3\ell)!(k-j)!i!j!\ell!}."
)

def _validate_style(style: str) -> str:
    normalized = style.lower()
    if normalized not in {"expanded", "factored"}:
        raise ValueError("style must be 'expanded' or 'factored'")
    return normalized


def format_expr(expr: Any, style: str = "expanded"):
    """Return an expression in the selected display style."""
    if _validate_style(style) == "factored":
        return sp.factor(expr)
    return sp.expand(expr)


def polynomial_to_latex(expr: Any, style: str = "expanded") -> str:
    """Format a SymPy polynomial as LaTeX in the selected style."""
    return sp.latex(format_expr(expr, style))


def polynomial_to_text(expr: Any, style: str = "expanded") -> str:
    """Format a SymPy polynomial as plain text in the selected style."""
    return str(format_expr(expr, style))


def matrix_to_latex(M: sp.MatrixBase) -> str:
    """Convert a SymPy matrix to a compact pmatrix LaTeX expression."""
    rows = []
    for i in range(M.rows):
        rows.append(" & ".join(sp.latex(sp.expand(M[i, j])) for j in range(M.cols)))
    return r"\begin{pmatrix}" + r"\\".join(rows) + r"\end{pmatrix}"


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
                "rod": format_expr(rod, style),
                "op": format_expr(op, style),
                "hyp": format_expr(hyp, style),
                "diff_rod_op": simplify(expand(rod - op)),
                "diff_op_hyp": simplify(expand(op - hyp)),
            }
        )
    return rows


def _latex_display(expression: str) -> list[str]:
    return [r"\[", expression, r"\]", ""]


def _vector_latex(n: int, rows: list[dict[str, Any]], key: str, label: str, style: str) -> str:
    components = r"\\".join(polynomial_to_latex(row[key], style) for row in rows)
    return rf"\mathbf Q_{n}^{{\mathrm{{{label}}}}}=\begin{{pmatrix}}{components}\end{{pmatrix}}"


def build_latex_export(n: int, rows: list[dict[str, Any]], style: str) -> str:
    """Build a LaTeX document fragment with formulas, matrix, vectors, and checks."""
    phi_n_latex = matrix_to_latex(Phi_second_kind(n))
    blocks = [
        f"% Krall--Sheffer formulas and polynomials for degree n={n}",
        r"\section*{Formulas used}",
        r"\subsection*{Basic data}",
        *_latex_display(PHI_AND_WEIGHT_LATEX),
        *_latex_display(L_OPERATOR_LATEX),
        *_latex_display(INDEXING_LATEX),
        r"\subsection*{Rodrigues formula}",
        *_latex_display(RODRIGUES_VECTOR_LATEX),
        *_latex_display(RODRIGUES_COMPONENT_LATEX),
        *_latex_display(GAUGE_DERIVATIVES_LATEX),
        r"These gauge derivatives are used because",
        *_latex_display(GAUGE_IDENTITY_LATEX),
        r"\subsection*{Second-kind Kronecker power}",
        *_latex_display(KRONECKER_VARIABLES_LATEX),
        r"The $(i,j)$-entry is defined by",
        *_latex_display(KRONECKER_DEFINITION_LATEX),
        *_latex_display(rf"\Phi^{{\{{{n}\}}}}={phi_n_latex}"),
        r"\subsection*{Operational formula}",
        *_latex_display(R_OPERATOR_LATEX),
        *_latex_display(OPERATIONAL_FORMULA_LATEX),
        *_latex_display(EXPONENTIAL_SERIES_LATEX),
        r"The series is finite on polynomials because $\mathcal R$ lowers total degree.",
        r"\subsection*{Hypergeometric-type expression}",
        *_latex_display(HYPER_FORMULA_LATEX),
        r"\section*{Polynomial vectors}",
        *_latex_display(_vector_latex(n, rows, "rod", "Rod", style)),
        *_latex_display(_vector_latex(n, rows, "op", "op", style)),
        *_latex_display(_vector_latex(n, rows, "hyp", "hyp", style)),
        r"\section*{Components and difference checks}",
    ]
    for row in rows:
        k = row["k"]
        blocks.extend(
            [
                *_latex_display(
                    rf"Q_{{{n},{k}}}^{{\mathrm{{Rod}}}} = {polynomial_to_latex(row['rod'], style)}"
                ),
                *_latex_display(
                    rf"Q_{{{n},{k}}}^{{\mathrm{{op}}}} = {polynomial_to_latex(row['op'], style)}"
                ),
                *_latex_display(
                    rf"Q_{{{n},{k}}}^{{\mathrm{{hyp}}}} = {polynomial_to_latex(row['hyp'], style)}"
                ),
                *_latex_display(
                    rf"Q_{{{n},{k}}}^{{\mathrm{{Rod}}}}-Q_{{{n},{k}}}^{{\mathrm{{op}}}}"
                    rf"={latex(row['diff_rod_op'])}."
                ),
                *_latex_display(
                    rf"Q_{{{n},{k}}}^{{\mathrm{{op}}}}-Q_{{{n},{k}}}^{{\mathrm{{hyp}}}}"
                    rf"={latex(row['diff_op_hyp'])}."
                ),
            ]
        )
    return "\n".join(blocks)


def build_markdown_export(n: int, rows: list[dict[str, Any]], style: str) -> str:
    """Build a Markdown document with formulas, matrix, vectors, and checks."""
    phi_n_latex = matrix_to_latex(Phi_second_kind(n))
    sections = [
        f"# Krall–Sheffer formulas and polynomials of degree {n}",
        "",
        "## Formulas used",
        "",
        "### Basic data",
        f"$${PHI_AND_WEIGHT_LATEX}$$",
        f"$${L_OPERATOR_LATEX}$$",
        f"$${INDEXING_LATEX}$$",
        "",
        "### Rodrigues formula",
        f"$${RODRIGUES_VECTOR_LATEX}$$",
        f"$${RODRIGUES_COMPONENT_LATEX}$$",
        f"$${GAUGE_DERIVATIVES_LATEX}$$",
        "These gauge derivatives are used because",
        f"$${GAUGE_IDENTITY_LATEX}$$",
        "",
        "### Second-kind Kronecker power",
        f"$${KRONECKER_VARIABLES_LATEX}$$",
        "The $(i,j)$-entry is the indicated coefficient:",
        f"$${KRONECKER_DEFINITION_LATEX}$$",
        rf"$$\Phi^{{\{{{n}\}}}}={phi_n_latex}$$",
        "",
        "### Operational formula",
        f"$${R_OPERATOR_LATEX}$$",
        f"$${OPERATIONAL_FORMULA_LATEX}$$",
        f"$${EXPONENTIAL_SERIES_LATEX}$$",
        "The sum is finite on polynomials because $\\mathcal R$ lowers total degree.",
        "",
        "### Hypergeometric-type expression",
        f"$${HYPER_FORMULA_LATEX}$$",
        "",
        "## Polynomial vectors",
        f"$${_vector_latex(n, rows, 'rod', 'Rod', style)}$$",
        f"$${_vector_latex(n, rows, 'op', 'op', style)}$$",
        f"$${_vector_latex(n, rows, 'hyp', 'hyp', style)}$$",
        "",
        "## Components and difference checks",
        "",
    ]
    for row in rows:
        k = row["k"]
        sections.extend(
            [
                f"### $Q_{{{n},{k}}}$",
                rf"$$Q_{{{n},{k}}}^{{\mathrm{{Rod}}}}={polynomial_to_latex(row['rod'], style)}$$",
                rf"$$Q_{{{n},{k}}}^{{\mathrm{{op}}}}={polynomial_to_latex(row['op'], style)}$$",
                rf"$$Q_{{{n},{k}}}^{{\mathrm{{hyp}}}}={polynomial_to_latex(row['hyp'], style)}$$",
                (
                    rf"$$Q_{{{n},{k}}}^{{\mathrm{{Rod}}}}-Q_{{{n},{k}}}^{{\mathrm{{op}}}}"
                    rf"={latex(row['diff_rod_op'])}.$$"
                ),
                (
                    rf"$$Q_{{{n},{k}}}^{{\mathrm{{op}}}}-Q_{{{n},{k}}}^{{\mathrm{{hyp}}}}"
                    rf"={latex(row['diff_op_hyp'])}.$$"
                ),
                "",
            ]
        )
    return "\n".join(sections)


def build_text_export(n: int, rows: list[dict[str, Any]], style: str) -> str:
    """Build a plain-text document with formulas, matrix, vectors, and checks."""
    lines = [
        f"Krall-Sheffer formulas and polynomials for degree n={n}",
        "",
        "FORMULAS USED",
        "Basic data:",
        "Phi = [[3*y, 1], [1, 0]]; omega(x,y) = exp(y**3 - x*y)",
        "L = 3*y*d_x^2 + 2*d_x*d_y - x*d_x - y*d_y",
        "Q_{n,k} corresponds to x**(n-k)*y**k, 0 <= k <= n.",
        "",
        "Rodrigues:",
        "Q_n^Rod(x,y)^t = omega^(-1) div^n(Phi^n omega)",
        "Q_{n,k}^Rod = sum_i binomial(n,i) (D_x^omega)^(n-i) (D_y^omega)^i ((Phi^n)_{i,k})",
        "D_x^omega(p) = d_x(p) - y*p; D_y^omega(p) = d_y(p) + (3*y**2-x)*p",
        "",
        "Second-kind Kronecker power:",
        "z1 = 3*y*t1 + t2; z2 = t1",
        "(Phi^n)_{i,j} is the coefficient of t1**(n-j)*t2**j in z1**(n-i)*z2**i.",
        f"Phi^{{{n}}} = {Phi_second_kind(n)}",
        "",
        "Operational:",
        "R = 3*y*d_x^2 + d_x*d_y - (1/2)*d_x^3",
        "Q_{n,k}^op = (-1)^n exp(-R)[binomial(n,k)*x**(n-k)*y**k]",
        "exp(-R)p = sum_{m>=0} (-1)^m R^m(p)/m! (finite on polynomials)",
        "",
        "Hypergeometric-type expression:",
        "Q_{n,k}^hyp = n! sum_{i,j,ell>=0; 2i+j+3ell<=n-k; j<=k} "
        "(-x)^(n-k-2i-j-3ell)*(-y)^(k-j)*(-3y)^i*(-1)^j*(-2)^ell / "
        "((n-k-2i-j-3ell)!*(k-j)!*i!*j!*ell!)",
        "",
        "POLYNOMIALS AND DIFFERENCE CHECKS",
    ]
    for row in rows:
        k = row["k"]
        lines.extend(
            [
                f"Q_{{{n},{k}}}^{{Rod}} = {polynomial_to_text(row['rod'], style)}",
                f"Q_{{{n},{k}}}^{{op}} = {polynomial_to_text(row['op'], style)}",
                f"Q_{{{n},{k}}}^{{hyp}} = {polynomial_to_text(row['hyp'], style)}",
                f"Q_{{{n},{k}}}^{{Rod}} - Q_{{{n},{k}}}^{{op}} = {row['diff_rod_op']}",
                f"Q_{{{n},{k}}}^{{op}} - Q_{{{n},{k}}}^{{hyp}} = {row['diff_op_hyp']}",
                "",
            ]
        )
    return "\n".join(lines)


def _render_phi_matrix(n: int) -> None:
    if n > 6:
        st.warning("For n > 6, the Kronecker power matrix may be wide.")
    with st.expander(f"Show the Kronecker power matrix Phi^{{{n}}}", expanded=(n <= 4)):
        phi_n = Phi_second_kind(n)
        st.latex(r"\Phi^{\{" + str(n) + r"\}}=" + matrix_to_latex(phi_n))
        st.caption(f"Matrix size: {phi_n.rows} × {phi_n.cols}.")


def _render_rodrigues_formula(n: int, include_component: bool = False) -> None:
    st.latex(RODRIGUES_VECTOR_LATEX)
    if include_component:
        st.latex(RODRIGUES_COMPONENT_LATEX)
        st.latex(GAUGE_DERIVATIVES_LATEX)
        st.markdown("These gauge derivatives are used because")
        st.latex(GAUGE_IDENTITY_LATEX)
    _render_phi_matrix(n)


def _render_operational_formula() -> None:
    st.latex(R_OPERATOR_LATEX)
    st.latex(OPERATIONAL_FORMULA_LATEX)
    st.latex(EXPONENTIAL_SERIES_LATEX)
    st.info(r"The sum is finite on polynomials because $\mathcal R$ lowers total degree.")


def _render_hyper_formula() -> None:
    st.latex(HYPER_FORMULA_LATEX)


def _render_formulas_used(n: int) -> None:
    st.header("Formulas used")

    st.subheader("A. Basic data")
    st.latex(PHI_AND_WEIGHT_LATEX)
    st.latex(L_OPERATOR_LATEX)
    st.latex(INDEXING_LATEX)

    st.subheader("B. Rodrigues formula")
    st.latex(RODRIGUES_VECTOR_LATEX)
    st.latex(RODRIGUES_COMPONENT_LATEX)
    st.latex(GAUGE_DERIVATIVES_LATEX)
    st.markdown("These gauge derivatives are used because")
    st.latex(GAUGE_IDENTITY_LATEX)

    st.subheader("C. Second-kind Kronecker power")
    st.markdown("Let")
    st.latex(KRONECKER_VARIABLES_LATEX)
    st.markdown(
        r"Then the $(i,j)$-entry of $\Phi^{n}$ is the coefficient of "
        r"$t_1^{n-j}t_2^j$ in $z_1^{n-i}z_2^i$."
    )
    st.latex(KRONECKER_DEFINITION_LATEX)
    _render_phi_matrix(n)

    st.subheader("D. Operational formula")
    _render_operational_formula()

    st.subheader("E. Hypergeometric-type expression")
    _render_hyper_formula()


def _show_vector(rows: list[dict[str, Any]], key: str, label: str, n: int, style: str) -> None:
    st.subheader(rf"$\mathbf Q_{n}^{{\mathrm{{{label}}}}}$")
    st.latex(_vector_latex(n, rows, key, label, style))
    for row in rows:
        st.markdown(rf"**$Q_{{{n},{row['k']}}}^{{\mathrm{{{label}}}}}$**")
        st.latex(polynomial_to_latex(row[key], style))


def _render_comparison(n: int, rows: list[dict[str, Any]]) -> None:
    st.latex(r"Q_{n,k}^{\mathrm{Rod}}-Q_{n,k}^{\mathrm{op}}")
    st.latex(r"Q_{n,k}^{\mathrm{op}}-Q_{n,k}^{\mathrm{hyp}}")
    all_zero = True
    for row in rows:
        k = row["k"]
        first = row["diff_rod_op"]
        second = row["diff_op_hyp"]
        st.latex(
            rf"Q_{{{n},{k}}}^{{\mathrm{{Rod}}}}-Q_{{{n},{k}}}^{{\mathrm{{op}}}}={latex(first)}"
        )
        st.latex(
            rf"Q_{{{n},{k}}}^{{\mathrm{{op}}}}-Q_{{{n},{k}}}^{{\mathrm{{hyp}}}}={latex(second)}"
        )
        if first != 0 or second != 0:
            all_zero = False
            st.error(f"The constructions differ for k = {k}.")
    if all_zero:
        st.success(f"All differences are zero for degree n = {n}; the three constructions agree.")


def _render_polynomial_tabs(n: int, rows: list[dict[str, Any]], style: str) -> None:
    st.header("Polynomial output")
    rod_tab, op_tab, hyp_tab, comparison_tab = st.tabs(
        ["Rodrigues", "Operational", "Hypergeometric", "Comparison"]
    )
    with rod_tab:
        _render_rodrigues_formula(n)
        _show_vector(rows, "rod", "Rod", n, style)
    with op_tab:
        _render_operational_formula()
        _show_vector(rows, "op", "op", n, style)
    with hyp_tab:
        _render_hyper_formula()
        _show_vector(rows, "hyp", "hyp", n, style)
    with comparison_tab:
        _render_comparison(n, rows)


def _render_downloads(n: int, latex_export: str, markdown_export: str, text_export: str) -> None:
    st.header("Downloads")
    columns = st.columns(3)
    columns[0].download_button(
        "Download formulas and polynomials as LaTeX",
        latex_export,
        file_name=f"Q_{n}_formulas_and_polynomials.tex",
        mime="application/x-tex",
        use_container_width=True,
    )
    columns[1].download_button(
        "Download formulas and polynomials as Markdown",
        markdown_export,
        file_name=f"Q_{n}_formulas_and_polynomials.md",
        mime="text/markdown",
        use_container_width=True,
    )
    columns[2].download_button(
        "Download plain text output",
        text_export,
        file_name=f"Q_{n}_formulas_and_polynomials.txt",
        mime="text/plain",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="∂", layout="wide")
    st.title(APP_TITLE)
    st.caption("Exact symbolic formulas and polynomial vectors for all three constructions.")

    with st.sidebar:
        st.header("Display controls")
        n = int(st.number_input("Degree n", min_value=0, max_value=MAX_DEGREE, value=3, step=1))
        style = st.radio("Output style", ["expanded", "factored"], horizontal=True)
        st.caption(f"Maximum supported interactive degree: n = {MAX_DEGREE}.")
        if n >= 7:
            st.warning("High degrees can take longer because all three constructions are computed exactly.")

    rows = compute_three_constructions(n, style)
    latex_export = build_latex_export(n, rows, style)
    markdown_export = build_markdown_export(n, rows, style)
    text_export = build_text_export(n, rows, style)

    _render_formulas_used(n)
    st.divider()
    _render_polynomial_tabs(n, rows, style)
    st.divider()
    _render_downloads(n, latex_export, markdown_export, text_export)


if __name__ == "__main__":
    main()
