"""Financing button (Founder, 2026-10): developers almost always borrow, so credit is a switch, not a study.
For-sale and develop-to-sell rental: thresholds are measured WITH debt (equity IRR and equity multiple).
Bridge (construction) loan: CONFIRMED by the Founder (2026-10-16) — banks lend on HARD construction costs only
(land and soft costs are equity). Draws a % of each month's hard cost, interest capitalised monthly, repaid from the first positive project cash flows (cash sweep), balance due at the end."""
from __future__ import annotations

# Base CONFIRMED by the Founder: the bank lends on the construction budget (hard costs) -> ltc 100% of hard costs.
# Cap from public bank terms (Banamex crédito puente: up to 65% of the project's sales value for medium/residential
# housing, 70% for economic housing). Rate HYPOTHESIS: TIIE + 3 to 6 points (public broker guide) ~ 12.5%.
DEFAULT_DEBT = dict(enabled=True, ltc=1.0, rate=0.125, sweep=1.0, base="hard construction costs",
                    max_pct_of_sales=0.65)


def apply(project: list[float], dev_costs: list[float], debt: dict | None) -> dict:
    d = {**DEFAULT_DEBT, **(debt or {})}
    if not d.get("enabled"):
        return dict(equity=list(project), peak_debt=0.0, interest=0.0, enabled=False)
    r = (1 + d["rate"]) ** (1 / 12) - 1
    cap = d.get("cap_amount")            # set by the protocol: max_pct_of_sales x sales value
    bal, peak, interest, eq, drawn = 0.0, 0.0, 0.0, [], 0.0
    for t, f in enumerate(project):
        i = bal * r; bal += i; interest += i
        draw = d["ltc"] * max(0.0, -dev_costs[t]) if t < len(dev_costs) else 0.0
        if cap is not None:
            draw = max(0.0, min(draw, cap - drawn))
        drawn += draw
        bal += draw
        e = f + draw
        if e > 0 and bal > 0:
            pay = min(bal, e * d["sweep"]); e -= pay; bal -= pay
        peak = max(peak, bal)
        eq.append(e)
    if bal > 1e-6:
        eq[-1] -= bal
    return dict(equity=eq, peak_debt=peak, interest=interest, enabled=True, ltc=d["ltc"], rate=d["rate"], base=d["base"],
                drawn=drawn, cap_amount=cap)
