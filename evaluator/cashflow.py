"""Monthly cash-flow helpers (pre-tax, unlevered)."""
from __future__ import annotations


def monthly_rate(annual: float) -> float:
    return (1 + annual) ** (1 / 12) - 1


def npv(rate_m: float, flows: list[float]) -> float:
    return sum(f / (1 + rate_m) ** t for t, f in enumerate(flows))


def irr_annual(flows: list[float]) -> float | None:
    """Annualised IRR from monthly flows, by bisection. None if no sign change."""
    if not (any(f < 0 for f in flows) and any(f > 0 for f in flows)):
        return None
    lo, hi = -0.99, 1.0
    f_lo, f_hi = npv(lo, flows), npv(hi, flows)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid, flows)
        if f_lo * f_mid <= 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (1 + (lo + hi) / 2) ** 12 - 1


def spread(total: float, start: int, months: int, length: int) -> list[float]:
    out = [0.0] * length
    months = max(1, months)
    for m in range(start, min(start + months, length)):
        out[m] += total / months
    return out


def add(*series: list[float]) -> list[float]:
    n = max(len(s) for s in series)
    return [sum(s[i] if i < len(s) else 0.0 for s in series) for i in range(n)]
