"""Symbolic verification tests for the most intriguing case."""

import os

from sympy import Rational, expand, factorial

from most_intriguing import (
    L_op,
    Q_from_generating,
    Q_hyper,
    Q_operational,
    Q_rodrigues,
    a_x,
    a_x_dag,
    a_y,
    a_y_dag,
    moment,
    x,
    y,
)


N = int(os.environ.get("MOST_INTRIGUING_N", "6"))
RUN_SLOW = os.environ.get("RUN_SLOW_MOST_INTRIGUING") == "1"


def assert_zero(expr):
    assert expand(expr) == 0


def test_regression_first_vectors():
    expected = {
        0: [1],
        1: [-x, -y],
        2: [x**2 - 6 * y, 2 * x * y - 2, y**2],
        3: [
            -x**3 + 18 * x * y - 12,
            -3 * x**2 * y + 18 * y**2 + 6 * x,
            -3 * x * y**2 + 6 * y,
            -y**3,
        ],
    }

    for n, vector in expected.items():
        for k, expected_component in enumerate(vector):
            assert_zero(Q_operational(n, k) - expected_component)
            assert_zero(Q_rodrigues(n, k) - expected_component)
            assert_zero(Q_hyper(n, k) - expected_component)


def test_three_constructions_agree_default_range():
    for n in range(N + 1):
        for k in range(n + 1):
            assert_zero(Q_rodrigues(n, k) - Q_operational(n, k))
            assert_zero(Q_operational(n, k) - Q_hyper(n, k))


def test_differential_equation_default_range():
    for n in range(N + 1):
        for k in range(n + 1):
            q = Q_operational(n, k)
            assert_zero(L_op(q) + n * q)


def test_generating_function_coefficients_default_range():
    for n in range(N + 1):
        for k in range(n + 1):
            assert_zero(Q_operational(n, k) - Q_from_generating(n, k))


def test_moment_functional_and_gram_matrix_default_range():
    for n in range(N + 1):
        for k in range(n + 1):
            q_nk = Q_operational(n, k)
            for m in range(N + 1):
                for j in range(m + 1):
                    value = moment(q_nk * Q_operational(m, j))
                    if n != m:
                        expected = 0
                    elif j == n - k:
                        expected = factorial(n) ** 2 / (factorial(n - k) * factorial(k))
                    else:
                        expected = 0
                    assert_zero(value - expected)


def test_ladder_operators_default_range():
    for n in range(N + 1):
        for k in range(n + 1):
            q = Q_operational(n, k)
            assert_zero(a_x_dag(q) - Rational(n - k + 1, n + 1) * Q_operational(n + 1, k))
            assert_zero(a_y_dag(q) - Rational(k + 1, n + 1) * Q_operational(n + 1, k + 1))
            assert_zero(a_x(q) - n * Q_operational(n - 1, k))
            assert_zero(a_y(q) - n * Q_operational(n - 1, k - 1))


def test_three_term_relations_default_range():
    for n in range(N + 1):
        for k in range(n + 1):
            q = Q_operational(n, k)
            x_rhs = (
                -Rational(n - k + 1, n + 1) * Q_operational(n + 1, k)
                + 6 * (k + 1) * Q_operational(n, k + 1)
                - n * Q_operational(n - 1, k - 1)
            )
            y_rhs = -Rational(k + 1, n + 1) * Q_operational(n + 1, k + 1) - n * Q_operational(n - 1, k)
            assert_zero(x * q - x_rhs)
            assert_zero(y * q - y_rhs)


def test_optional_slow_degree_8():
    if not RUN_SLOW:
        return

    for n in range(9):
        for k in range(n + 1):
            assert_zero(Q_rodrigues(n, k) - Q_operational(n, k))
            assert_zero(Q_operational(n, k) - Q_hyper(n, k))
            assert_zero(L_op(Q_operational(n, k)) + n * Q_operational(n, k))
            assert_zero(Q_operational(n, k) - Q_from_generating(n, k))


def test_show_three_constructions_plain_cli_labels_and_polynomial():
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "show_three_constructions.py", "--degree", "3", "--format", "plain"],
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout
    assert "Q_{3,0}^{Rod}" in output
    assert "Q_{3,0}^{op}" in output
    assert "Q_{3,0}^{hyp}" in output
    assert "-x**3 + 18*x*y - 12" in output


def test_streamlit_helper_degree_three_contains_expected_polynomial():
    from streamlit_app import compute_three_constructions

    rows = compute_three_constructions(3, "expanded")
    expected = -x**3 + 18 * x * y - 12

    assert expand(rows[0]["rod"] - expected) == 0
    assert expand(rows[0]["op"] - expected) == 0
    assert expand(rows[0]["hyp"] - expected) == 0


def test_latex_export_degree_three_contains_formulas_matrix_and_polynomials():
    from streamlit_app import HYPER_FORMULA_LATEX, build_latex_export, compute_three_constructions

    rows = compute_three_constructions(3, "expanded")
    output = build_latex_export(3, rows, "expanded")

    assert r"\Phi^{\{3\}}" in output
    assert r"Q_{n,k}^{\mathrm{Rod}}" in output
    assert r"Q_{n,k}^{\mathrm{op}}" in output
    assert HYPER_FORMULA_LATEX in output
    assert r"Q_{3,0}^{\mathrm{Rod}}" in output
    assert r"Q_{3,0}^{\mathrm{op}}" in output
    assert r"Q_{3,0}^{\mathrm{hyp}}" in output
    assert r"- x^{3} + 18 x y - 12" in output
    assert "\\" + "qquad" not in output
    assert r"\sum_{n\geq0}\frac{1}{n!}\sum_{k=0}^n" not in output
    assert r"\exp(-ax-by-3a^2y" + "-ab-2a^3)" not in output
    assert "Ho" + "rn" not in output


def test_all_streamlit_exports_keep_required_content_and_omit_removed_content():
    from streamlit_app import (
        build_latex_export,
        build_markdown_export,
        build_text_export,
        compute_three_constructions,
    )

    rows = compute_three_constructions(3, "expanded")
    outputs = [
        build_latex_export(3, rows, "expanded"),
        build_markdown_export(3, rows, "expanded"),
        build_text_export(3, rows, "expanded"),
    ]

    for output in outputs:
        assert "Rod" in output
        assert "op" in output
        assert "hyp" in output
        assert "Hypergeometric-type expression" in output
        assert "2i+j+3" in output
        assert "j" in output and "k" in output
        assert "Ho" + "rn" not in output
        assert "Generating function" not in output
        assert "exp(-ax-by-3a^2y" + "-ab-2a^3)" not in output
        assert "exp(-a*x-b*y-3*a**2*y" + "-a*b-2*a**3)" not in output


def test_streamlit_app_uses_clean_hypergeometric_label_and_no_removed_formula():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file("streamlit_app.py", default_timeout=30).run()
    latex_output = "\n".join(element.value for element in app.latex)

    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "Rodrigues",
        "Operational",
        "Hypergeometric",
        "Comparison",
    ]
    assert "E. Hypergeometric-type expression" in [heading.value for heading in app.subheader]
    assert r"Q_{n,k}^{\mathrm{hyp}}(x,y)=n!" in latex_output
    assert "\\" + "qquad" not in latex_output
    assert "Ho" + "rn" not in latex_output
    assert "exp(-ax-by-3a^2y" + "-ab-2a^3)" not in latex_output


def test_matrix_to_latex_for_second_kind_degree_two():
    from most_intriguing import Phi_second_kind
    from streamlit_app import matrix_to_latex

    output = matrix_to_latex(Phi_second_kind(2))

    assert r"9 y^{2} & 6 y & 1" in output
    assert r"3 y & 1 & 0" in output
    assert r"1 & 0 & 0" in output
    assert output == (
        r"\begin{pmatrix}9 y^{2} & 6 y & 1\\"
        r"3 y & 1 & 0\\1 & 0 & 0\end{pmatrix}"
    )
