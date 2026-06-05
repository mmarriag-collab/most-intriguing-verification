"""Print explicit polynomial vectors for the most intriguing case."""

from __future__ import annotations

import argparse
from pathlib import Path

from sympy import latex, sstr

from most_intriguing import Q_hyper, Q_operational, Q_rodrigues


CONSTRUCTIONS = {
    "operational": Q_operational,
    "rodrigues": Q_rodrigues,
    "hyper": Q_hyper,
}


def polynomial_vector(degree: int, method: str = "operational"):
    """Return [Q_{n,0}, ..., Q_{n,n}] for the selected construction."""
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    try:
        constructor = CONSTRUCTIONS[method]
    except KeyError as exc:
        choices = ", ".join(sorted(CONSTRUCTIONS))
        raise ValueError(f"method must be one of: {choices}") from exc
    return [constructor(degree, k) for k in range(degree + 1)]


def format_vector(degree: int, vector, output_format: str = "latex") -> str:
    """Format Q_n as either plain text or LaTeX."""
    if output_format == "plain":
        lines = [f"Q_{degree}(x,y) = ("]
        for k, polynomial in enumerate(vector):
            comma = "," if k < degree else ""
            lines.append(f"  Q_{{{degree},{k}}} = {sstr(polynomial)}{comma}")
        lines.append(")^t")
        return "\n".join(lines)

    if output_format == "latex":
        entries = " \\\\\n".join(latex(polynomial) for polynomial in vector)
        return (
            "\\[\n"
            f"\\mathbf Q_{degree}(x,y)=\n"
            "\\begin{pmatrix}\n"
            f"{entries}\n"
            "\\end{pmatrix}.\n"
            "\\]"
        )

    raise ValueError("format must be either plain or latex")


def render_polynomial_vector(degree: int, method: str = "operational", output_format: str = "latex") -> str:
    """Build the formatted vector for command-line use and tests."""
    return format_vector(degree, polynomial_vector(degree, method), output_format)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print Q_n for the Krall-Sheffer most intriguing case.")
    parser.add_argument("--degree", type=int, required=True, help="Degree n of the vector Q_n.")
    parser.add_argument(
        "--method",
        choices=sorted(CONSTRUCTIONS),
        default="operational",
        help="Construction method to use.",
    )
    parser.add_argument(
        "--format",
        choices=["latex", "plain"],
        default="latex",
        help="Output format.",
    )
    parser.add_argument("--output", type=Path, help="Optional file path for the generated output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = render_polynomial_vector(args.degree, args.method, args.format)

    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
