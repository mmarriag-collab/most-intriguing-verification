"""Symbolic identities for the Krall-Sheffer most intriguing case.

The module uses exact SymPy arithmetic throughout.  The component Q_{n,k}
corresponds to the monomial x**(n-k) y**k, for 0 <= k <= n.
"""

from __future__ import annotations

from functools import lru_cache

from sympy import Matrix, Rational, binomial, diff, expand, factorial, poly, symbols
from sympy.abc import a, b, x, y


t1, t2 = symbols("t1 t2")


Phi = Matrix([[3 * y, 1], [1, 0]])
ONE_HALF = Rational(1, 2)


def _valid_index(n: int, k: int) -> bool:
    return n >= 0 and 0 <= k <= n


@lru_cache(maxsize=None)
def Phi_second_kind(n: int) -> Matrix:
    """Return the second-kind Kronecker power Phi^{n}.

    If z1 = Phi[0,0]*t1 + Phi[0,1]*t2 and
    z2 = Phi[1,0]*t1 + Phi[1,1]*t2, the (i,j) entry is the coefficient of
    t1**(n-j) t2**j in z1**(n-i) z2**i.
    """
    if n < 0:
        raise ValueError("n must be nonnegative")
    if n == 0:
        return Matrix([[1]])

    z1 = Phi[0, 0] * t1 + Phi[0, 1] * t2
    z2 = Phi[1, 0] * t1 + Phi[1, 1] * t2
    rows = []
    for i in range(n + 1):
        expr = expand(z1 ** (n - i) * z2**i)
        rows.append([expand(expr).coeff(t1, n - j).coeff(t2, j) for j in range(n + 1)])
    return Matrix(rows)


def Dx_omega(p):
    """Gauge derivative (1/omega) d_x(p omega)."""
    return expand(diff(p, x) - y * p)


def Dy_omega(p):
    """Gauge derivative (1/omega) d_y(p omega)."""
    return expand(diff(p, y) + (3 * y**2 - x) * p)


def _iterate_operator(op, p, count: int):
    result = p
    for _ in range(count):
        result = op(result)
    return expand(result)


@lru_cache(maxsize=None)
def Q_rodrigues(n: int, k: int):
    """Rodrigues construction of Q_{n,k}.

    We apply Dy_omega first and then Dx_omega.  These conjugated partial
    derivatives commute because they come from conjugating ordinary partials
    by the same weight omega, so the convention is immaterial but fixed.
    """
    if not _valid_index(n, k):
        return 0

    phi_n = Phi_second_kind(n)
    total = 0
    for i in range(n + 1):
        term = phi_n[i, k]
        term = _iterate_operator(Dy_omega, term, i)
        term = _iterate_operator(Dx_omega, term, n - i)
        total += binomial(n, i) * term
    return expand(total)


def R_op(p):
    """Operational differential operator R."""
    return expand(3 * y * diff(p, x, 2) + diff(p, x, y) - ONE_HALF * diff(p, x, 3))


def exp_minus_R(p):
    """Finite action of exp(-R) on a polynomial."""
    total = p
    current = p
    m = 1
    while True:
        current = R_op(current)
        if expand(current) == 0:
            break
        total += (-1) ** m * current / factorial(m)
        m += 1
    return expand(total)


@lru_cache(maxsize=None)
def Q_operational(n: int, k: int):
    """Operational construction of Q_{n,k}."""
    if not _valid_index(n, k):
        return 0
    seed = binomial(n, k) * x ** (n - k) * y**k
    return expand((-1) ** n * exp_minus_R(seed))


@lru_cache(maxsize=None)
def Q_hyper(n: int, k: int):
    """Finite hypergeometric/Horn formula for Q_{n,k}."""
    if not _valid_index(n, k):
        return 0

    total = 0
    for i in range(n + 1):
        for j in range(k + 1):
            for ell in range(n + 1):
                remaining = n - k - 2 * i - j - 3 * ell
                if remaining < 0:
                    continue
                term = (
                    (-x) ** remaining
                    * (-y) ** (k - j)
                    * (-3 * y) ** i
                    * (-1) ** j
                    * (-2) ** ell
                )
                term /= (
                    factorial(remaining)
                    * factorial(k - j)
                    * factorial(i)
                    * factorial(j)
                    * factorial(ell)
                )
                total += term
    return expand(factorial(n) * total)


def L_op(p):
    """Krall-Sheffer differential operator L."""
    return expand(3 * y * diff(p, x, 2) + 2 * diff(p, x, y) - x * diff(p, x) - y * diff(p, y))


def generating_function():
    """Return G(a,b;x,y)."""
    from sympy import exp

    return exp(-a * x - b * y - 3 * a**2 * y - a * b - 2 * a**3)


def Q_from_generating(n: int, k: int):
    """Coefficient extraction from the finite Taylor data of G."""
    if not _valid_index(n, k):
        return 0

    # Since only the coefficient of a**(n-k) b**k is needed, truncate the
    # exponential series at total degree n in a,b by expanding the polynomial
    # exponent to powers 0..n.
    exponent = -a * x - b * y - 3 * a**2 * y - a * b - 2 * a**3
    truncated = sum(exponent**r / factorial(r) for r in range(n + 1))
    coeff = expand(truncated).coeff(a, n - k).coeff(b, k)
    return expand(factorial(n) * coeff)


def moment_monomial(A: int, B: int):
    """Moment functional on x**A y**B."""
    if A >= B and (A - B) % 3 == 0:
        return factorial(A) / factorial((A - B) // 3)
    return 0


def moment(poly_expr):
    """Extend the moment functional linearly to a polynomial."""
    expr = expand(poly_expr)
    if expr == 0:
        return 0

    result = 0
    for (A, B), coeff in poly(expr, x, y).terms():
        result += coeff * moment_monomial(A, B)
    return expand(result)


def a_x_dag(p):
    return expand(-x * p + 6 * y * diff(p, x) + diff(p, y) - 3 * diff(p, x, 2))


def a_y_dag(p):
    return expand(diff(p, x) - y * p)


def a_x(p):
    return expand(-diff(p, x))


def a_y(p):
    return expand(-diff(p, y) - 3 * diff(p, x, 2))
