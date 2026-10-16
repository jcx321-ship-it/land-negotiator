"""Financing button (Founder, 2026-10): developers almost always borrow, so credit is a switch, not a study.
For-sale and develop-to-sell rental: thresholds are measured WITH debt (equity IRR and equity multiple).
Simple construction loan: draws a % of each month's development cost (land is never financed), interest
capitalised monthly, repaid from the first positive project cash flows (cash sweep), balance due at the end."""
from __future__ import annotations

DEFAULT_DEBT = dict(enabled=True, ltc=0.65, rate=0.125, sweep=1.0)  # HYPOTHESIS: 65% of dev. cost, ~TIIE+4; Founder to confirm


def apply(project: list[float], dev_costs: list[float], debt: dict | None) -> dict:
    d = {**DEFAULT_DEBT, **(debt or {})}
    if not d.get("enabled"):
        return dict(equity=list(project), peak_debt=0.0, interest=0.0, enabled=False)
    r = (1 + d["rate"]) ** (1 / 12) - 1
    bal, peak, interest, eq = 0.0, 0.0, 0.0, []
    for t, f in enumerate(project):
        i = bal * r; bal += i; interest += i
        draw = d["ltc"] * max(0.0, -dev_costs[t]) if t < len(dev_costs) else 0.0
        bal += draw
        e = f + draw
        if e > 0 and bal > 0:
            pay = min(bal, e * d["sweep"]); e -= pay; bal -= pay
        peak = max(peak, bal)
        eq.append(e)
    if bal > 1e-6:
        eq[-1] -= bal
    return dict(equity=eq, peak_debt=peak, interest=interest, enabled=True, ltc=d["ltc"], rate=d["rate"])
