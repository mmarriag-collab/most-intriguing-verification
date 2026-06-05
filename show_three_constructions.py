"""Display the three explicit constructions of Q_{n,k}."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from sympy import expand, factor, latex, simplify, sstr

from most_intriguing import Q_hyper, Q_operational, Q_rodrigues


@dataclass(frozen=True)
class ConstructionRow:
    """One displayed row for a fixed k."""

    k: int
    rodrigues: object
    operational: object
    hyper: object
    rod_minus_op: object
    op_minus_hyp: object


def _display_expr(expr, *, factored: bool):
    """Return the expression form requested for display columns."""
    if factored:
        return factor(expr)
    return expand(expr)


def construction_rows(degree: int, *, factored: bool = False) -> list[ConstructionRow]:
    """Return separately computed construction rows for k = 0, ..., n."""
    if degree < 0:
        raise ValueError("degree must be nonnegative")

    rows = []
    for k in range(degree + 1):
        rodrigues_raw = Q_rodrigues(degree, k)
        operational_raw = Q_operational(degree, k)
        hyper_raw = Q_hyper(degree, k)
        rows.append(
            ConstructionRow(
                k=k,
                rodrigues=_display_expr(rodrigues_raw, factored=factored),
                operational=_display_expr(operational_raw, factored=factored),
                hyper=_display_expr(hyper_raw, factored=factored),
                rod_minus_op=simplify(expand(rodrigues_raw - operational_raw)),
                op_minus_hyp=simplify(expand(operational_raw - hyper_raw)),
            )
        )
    return rows


def _intro(degree: int) -> str:
    return f"Q_{{n,k}} corresponds to x^(n-k) y^k, 0 <= k <= n. Here n = {degree}."


def format_plain(degree: int, rows: list[ConstructionRow]) -> str:
    """Format construction rows as readable plain text."""
    lines = [
        _intro(degree),
        "",
        "k | Q_{n,k}^{Rod} | Q_{n,k}^{op} | Q_{n,k}^{hyp} | Rod - op | op - hyp",
        "- | -------------- | ------------ | ------------- | -------- | --------",
    ]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    str(row.k),
                    f"Q_{{{degree},{row.k}}}^{{Rod}} = {sstr(row.rodrigues)}",
                    f"Q_{{{degree},{row.k}}}^{{op}} = {sstr(row.operational)}",
                    f"Q_{{{degree},{row.k}}}^{{hyp}} = {sstr(row.hyper)}",
                    sstr(row.rod_minus_op),
                    sstr(row.op_minus_hyp),
                ]
            )
        )
    return "\n".join(lines)


def format_markdown(degree: int, rows: list[ConstructionRow]) -> str:
    """Format construction rows as a Markdown table."""
    lines = [
        _intro(degree),
        "",
        "| k | Q_{n,k}^{Rod} | Q_{n,k}^{op} | Q_{n,k}^{hyp} | Rod - op | op - hyp |",
        "|---:|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.k),
                    f"`Q_{{{degree},{row.k}}}^{{Rod}} = {sstr(row.rodrigues)}`",
                    f"`Q_{{{degree},{row.k}}}^{{op}} = {sstr(row.operational)}`",
                    f"`Q_{{{degree},{row.k}}}^{{hyp}} = {sstr(row.hyper)}`",
                    f"`{sstr(row.rod_minus_op)}`",
                    f"`{sstr(row.op_minus_hyp)}`",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def format_latex(degree: int, rows: list[ConstructionRow]) -> str:
    """Format construction rows as a LaTeX array fragment."""
    body = []
    for row in rows:
        body.append(
            " & ".join(
                [
                    str(row.k),
                    latex(row.rodrigues),
                    latex(row.operational),
                    latex(row.hyper),
                    latex(row.rod_minus_op),
                    latex(row.op_minus_hyp),
                ]
            )
            + r"\\"
        )

    return "\n".join(
        [
            r"\[",
            rf"\text{{Indexing: }} Q_{{n,k}} \leftrightarrow x^{{n-k}} y^k,\quad 0 \le k \le n,\quad n={degree}.",
            r"\]",
            r"\[",
            r"\begin{array}{c|c|c|c|c|c}",
            rf"k & Q_{{{degree},k}}^{{\mathrm{{Rod}}}} & Q_{{{degree},k}}^{{\mathrm{{op}}}} & Q_{{{degree},k}}^{{\mathrm{{hyp}}}} & Q_{{{degree},k}}^{{\mathrm{{Rod}}}}-Q_{{{degree},k}}^{{\mathrm{{op}}}} & Q_{{{degree},k}}^{{\mathrm{{op}}}}-Q_{{{degree},k}}^{{\mathrm{{hyp}}}}\\",
            r"\hline",
            *body,
            r"\end{array}",
            r"\]",
        ]
    )


def format_latex_blocks(degree: int, rows: list[ConstructionRow]) -> str:
    """Format construction rows as one LaTeX display block per expression."""
    lines = [
        r"\[",
        rf"\text{{Indexing: }} Q_{{n,k}} \leftrightarrow x^{{n-k}} y^k,\quad 0 \le k \le n,\quad n={degree}.",
        r"\]",
    ]
    for row in rows:
        lines.extend(
            [
                r"\[",
                rf"Q_{{{degree},{row.k}}}^{{\mathrm{{Rod}}}}={latex(row.rodrigues)}",
                r"\]",
                r"\[",
                rf"Q_{{{degree},{row.k}}}^{{\mathrm{{op}}}}={latex(row.operational)}",
                r"\]",
                r"\[",
                rf"Q_{{{degree},{row.k}}}^{{\mathrm{{hyp}}}}={latex(row.hyper)}",
                r"\]",
                r"\[",
                rf"Q_{{{degree},{row.k}}}^{{\mathrm{{Rod}}}}-Q_{{{degree},{row.k}}}^{{\mathrm{{op}}}}={latex(row.rod_minus_op)},\qquad",
                rf"Q_{{{degree},{row.k}}}^{{\mathrm{{op}}}}-Q_{{{degree},{row.k}}}^{{\mathrm{{hyp}}}}={latex(row.op_minus_hyp)}.",
                r"\]",
            ]
        )
    return "\n".join(lines)


FORMATTERS = {
    "latex": format_latex,
    "latex_blocks": format_latex_blocks,
    "markdown": format_markdown,
    "plain": format_plain,
}


def render_three_constructions(degree: int, output_format: str = "latex", *, factored: bool = False) -> str:
    """Render the three explicit constructions and their simplified differences."""
    try:
        formatter = FORMATTERS[output_format]
    except KeyError as exc:
        choices = ", ".join(sorted(FORMATTERS))
        raise ValueError(f"format must be one of: {choices}") from exc
    return formatter(degree, construction_rows(degree, factored=factored))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Display all three constructions of Q_{n,k}.")
    parser.add_argument("--degree", type=int, default=3, help="Degree n of the vector Q_n.")
    parser.add_argument(
        "--format",
        choices=sorted(FORMATTERS),
        default="latex",
        help="Output format.",
    )
    parser.add_argument("--output", type=Path, help="Optional file path for the generated output.")
    expression_group = parser.add_mutually_exclusive_group()
    expression_group.add_argument(
        "--expanded",
        action="store_true",
        help="Print expanded polynomial expressions (default).",
    )
    expression_group.add_argument(
        "--factored",
        action="store_true",
        help="Print factored polynomial expressions when possible.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = render_three_constructions(args.degree, args.format, factored=args.factored)

    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
