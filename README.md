# Krall-Sheffer Most Intriguing Case

This is a self-contained symbolic verification project for the Krall-Sheffer
"most intriguing case" of bivariate orthogonal polynomials.  It uses exact
SymPy expressions only; there is no floating point arithmetic.

## Indexing

The component `Q_{n,k}` corresponds to the monomial `x**(n-k) y**k`, with
`0 <= k <= n`.

Thus the vector is

```text
Q_n = (Q_{n,0}, Q_{n,1}, ..., Q_{n,n})^t.
```

This matches the Rodrigues-paper convention
`Q_n^t = (Q_{n,0}, Q_{n-1,1}, ..., Q_{0,n})`.

## Three Constructions

The implementation compares three exact constructions of the same polynomial:

1. Matrix Rodrigues formula using the second-kind Kronecker power `Phi^{n}`.
   The gauge derivatives are applied in the fixed order `Dy_omega` first, then
   `Dx_omega`; these commute because both are conjugated ordinary partial
   derivatives for the same weight.
2. Operational formula
   `Q_{n,k} = (-1)^n exp(-R)[binomial(n,k) x**(n-k) y**k]`, where the
   exponential is finite on polynomials.
3. Hypergeometric/Horn finite formula, implemented as an exact finite sum.


## Displaying the three constructions

Use `show_three_constructions.py` to print the separately computed Matrix
Rodrigues, operational, and hypergeometric/Horn formulas for every
`k = 0, 1, ..., n` in one selected degree.  The output includes the expanded
and simplified difference columns `Rod - op` and `op - hyp`, so matching
formulas still show all three symbolic expressions rather than suppressing
duplicates.

By default, the script uses `--degree 3`, `--format latex`, and expanded
polynomial expressions.  Use `--factored` to display factored forms when SymPy
can factor them.  The `latex_blocks` format is recommended for larger degrees
because it prints one display block per construction.

Examples:

```bash
python show_three_constructions.py --degree 3 --format plain
python show_three_constructions.py --degree 4 --format latex_blocks --output Q4.tex
python show_three_constructions.py --degree 5 --format markdown --output Q5.md
```

## Running Tests

Install dependencies and run:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

GitHub Actions is configured in `.github/workflows/python-tests.yml`, so tests
can also run on GitHub without requiring Python on your computer.

## Default Degree

The default test suite verifies all identities for `0 <= k <= n <= 6`.

An optional higher-degree check up to `N=8` is included.  It is disabled by
default because symbolic Rodrigues and Gram-matrix checks get expensive.  To run
the optional slow construction/eigenvalue/generating-function check:

```bash
RUN_SLOW_MOST_INTRIGUING=1 python -m pytest -q
```

You can also change the default limit:

```bash
MOST_INTRIGUING_N=8 python -m pytest -q
```

## Scope

This project is a symbolic verification tool.  Passing tests provide strong
computer-algebra evidence for the listed identities through the selected degree,
but this is not a replacement for a mathematical proof.
