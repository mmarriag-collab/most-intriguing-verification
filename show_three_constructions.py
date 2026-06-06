"""Display the three explicit constructions of Q_{n,k} side by side."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from sympy import expand, factor, latex, simplify, sstr

from most_intriguing import Q_hyper, Q_operational, Q_rodrigues


@dataclass(frozen=True)
class ConstructionRow:
    """One display row for fixed n and k."""

    k: int
    rodrigues: object
    operational: object
    hyper: object
    rod_minus_op: object
    op_minus_hyp: object


FORMAT_CHOICES = ["latex", "latex_blocks", "markdown", "plain"]


def _display_expr(expr, expression_style: str):
    """Return an expression transformed only for display."""
    if expression_style == "factored":
        return factor(expr)
    return expand(expr)


def construction_rows(degree: int, expression_style: str = "expanded") -> list[ConstructionRow]:
    """Compute table rows from all three construction functions for degree n."""
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if expression_style not in {"expanded", "factored"}:
        raise ValueError("expression_style must be 'expanded' or 'factored'")

    rows: list[ConstructionRow] = []
    for k in range(degree + 1):
        rod_raw = Q_rodrigues(degree, k)
        op_raw = Q_operational(degree, k)
        hyp_raw = Q_hyper(degree, k)
        rows.append(
            ConstructionRow(
                k=k,
                rodrigues=_display_expr(rod_raw, expression_style),
                operational=_display_expr(op_raw, expression_style),
                hyper=_display_expr(hyp_raw, expression_style),
                rod_minus_op=simplify(expand(rod_raw - op_raw)),
                op_minus_hyp=simplify(expand(op_raw - hyp_raw)),
            )
        )
    return rows


def _plain_row(degree: int, row: ConstructionRow) -> str:
    cells = [
        str(row.k),
        f"Q_{{{degree},{row.k}}}^{{Rod}} = {sstr(row.rodrigues)}",
        f"Q_{{{degree},{row.k}}}^{{op}} = {sstr(row.operational)}",
        f"Q_{{{degree},{row.k}}}^{{hyp}} = {sstr(row.hyper)}",
        f"{sstr(row.rod_minus_op)}",
        f"{sstr(row.op_minus_hyp)}",
    ]
    return " | ".join(cells)


def render_plain(degree: int, rows: list[ConstructionRow]) -> str:
    """Render a plain-text table."""
    lines = [
        f"Degree n = {degree}",
        "Q_{n,k} corresponds to x^{n-k} y^k, 0 <= k <= n.",
        "k | Q_{n,k}^{Rod} | Q_{n,k}^{op} | Q_{n,k}^{hyp} | Rod - op | op - hyp",
        "- | ------------- | ------------ | ------------- | -------- | --------",
    ]
    lines.extend(_plain_row(degree, row) for row in rows)
    return "\n".join(lines)


def _markdown_row(degree: int, row: ConstructionRow) -> str:
    cells = [
        str(row.k),
        f"`Q_{{{degree},{row.k}}}^{{Rod}} = {sstr(row.rodrigues)}`",
        f"`Q_{{{degree},{row.k}}}^{{op}} = {sstr(row.operational)}`",
        f"`Q_{{{degree},{row.k}}}^{{hyp}} = {sstr(row.hyper)}`",
        f"`{sstr(row.rod_minus_op)}`",
        f"`{sstr(row.op_minus_hyp)}`",
    ]
    return "| " + " | ".join(cells) + " |"


def render_markdown(degree: int, rows: list[ConstructionRow]) -> str:
    """Render a Markdown table."""
    lines = [
        f"# Three constructions for degree {degree}",
        "",
        "Indexing convention: `Q_{n,k}` corresponds to `x^{n-k} y^k`, `0 <= k <= n`.",
        "",
        "| k | Q_{n,k}^{Rod} | Q_{n,k}^{op} | Q_{n,k}^{hyp} | Rod - op | op - hyp |",
        "|---:|---|---|---|---|---|",
    ]
    lines.extend(_markdown_row(degree, row) for row in rows)
    return "\n".join(lines)


def render_latex_table(degree: int, rows: list[ConstructionRow]) -> str:
    """Render a LaTeX array table fragment."""
    lines = [
        "\\[",
        "\\begin{array}{c|c|c|c|c|c}",
        f"\\multicolumn{{6}}{{c}}{{Q_{{n,k}}\\text{{ corresponds to }}x^{{n-k}}y^k,\\ 0\\le k\\le n,\\ n={degree}}}\\\\",
        "k & Q_{n,k}^{\\mathrm{Rod}} & Q_{n,k}^{\\mathrm{op}} & Q_{n,k}^{\\mathrm{hyp}} "
        "& Q_{n,k}^{\\mathrm{Rod}}-Q_{n,k}^{\\mathrm{op}} "
        "& Q_{n,k}^{\\mathrm{op}}-Q_{n,k}^{\\mathrm{hyp}}\\\\",
        "\\hline",
    ]
    for row in rows:
        lines.append(
            f"{row.k} & {latex(row.rodrigues)} & {latex(row.operational)} & {latex(row.hyper)} "
            f"& {latex(row.rod_minus_op)} & {latex(row.op_minus_hyp)}\\\\"
        )
    lines.extend(["\\end{array}", "\\]"])
    return "\n".join(lines)


def render_latex_blocks(degree: int, rows: list[ConstructionRow]) -> str:
    """Render one LaTeX display block per construction and k."""
    lines = [
        f"% Q_{{n,k}} corresponds to x^{{n-k}} y^k, 0 <= k <= n; n={degree}.",
    ]
    for row in rows:
        lines.extend(
            [
                "\\[",
                f"Q_{{{degree},{row.k}}}^{{\\mathrm{{Rod}}}}={latex(row.rodrigues)}",
                "\\]",
                "\\[",
                f"Q_{{{degree},{row.k}}}^{{\\mathrm{{op}}}}={latex(row.operational)}",
                "\\]",
                "\\[",
                f"Q_{{{degree},{row.k}}}^{{\\mathrm{{hyp}}}}={latex(row.hyper)}",
                "\\]",
                "\\[",
                f"Q_{{{degree},{row.k}}}^{{\\mathrm{{Rod}}}}-Q_{{{degree},{row.k}}}^{{\\mathrm{{op}}}}={latex(row.rod_minus_op)}.",
                "\\]",
                "\\[",
                f"Q_{{{degree},{row.k}}}^{{\\mathrm{{op}}}}-Q_{{{degree},{row.k}}}^{{\\mathrm{{hyp}}}}={latex(row.op_minus_hyp)}.",
                "\\]",
            ]
        )
    return "\n".join(lines)


def render_three_constructions(degree: int, output_format: str = "latex", expression_style: str = "expanded") -> str:
    """Build formatted output for all three constructions."""
    rows = construction_rows(degree, expression_style)
    if output_format == "plain":
        return render_plain(degree, rows)
    if output_format == "markdown":
        return render_markdown(degree, rows)
    if output_format == "latex":
        return render_latex_table(degree, rows)
    if output_format == "latex_blocks":
        return render_latex_blocks(degree, rows)
    choices = ", ".join(FORMAT_CHOICES)
    raise ValueError(f"format must be one of: {choices}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Display Q_{n,k} from Rodrigues, operational, and hypergeometric formulas.")
    parser.add_argument("--degree", type=int, default=3, help="Degree n. Defaults to 3.")
    parser.add_argument("--format", choices=FORMAT_CHOICES, default="latex", help="Output format. Defaults to latex.")
    parser.add_argument("--output", type=Path, help="Optional file path for the generated output.")
    style_group = parser.add_mutually_exclusive_group()
    style_group.add_argument("--expanded", action="store_const", const="expanded", dest="expression_style", help="Display expanded polynomial expressions. This is the default.")
    style_group.add_argument("--factored", action="store_const", const="factored", dest="expression_style", help="Display factored polynomial expressions when possible.")
    parser.set_defaults(expression_style="expanded")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = render_three_constructions(args.degree, args.format, args.expression_style)

    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
