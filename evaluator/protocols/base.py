from __future__ import annotations
from ..cashflow import monthly_rate, npv, irr_annual
from ..criteria import TARGET_IRR_PRETAX, MIN_EQUITY_MULTIPLE
from .. import debt as debt_mod


def solve_land_price(flows_fn, target: float = TARGET_IRR_PRETAX) -> float:
    """flows_fn(P) -> monthly flows, linear in P. Returns the land price that makes NPV = 0 at the target IRR."""
    r = monthly_rate(target)
    a = npv(r, flows_fn(0.0))
    b = npv(r, flows_fn(1.0)) - a
    return -a / b if b != 0 else float("nan")


def summarize(flows: list[float]) -> dict:
    inflow = sum(f for f in flows if f > 0)
    outflow = -sum(f for f in flows if f < 0)
    cum, peak = 0.0, 0.0
    for f in flows:
        cum += f
        peak = min(peak, cum)
    return dict(irr=irr_annual(flows), profit=inflow - outflow,
                multiple=(inflow / outflow) if outflow else None, peak_equity=-peak)


def solve_with_hurdles(flows_fn, dev_costs, debt: dict | None, target_irr: float = TARGET_IRR_PRETAX,
                       min_multiple: float | None = None) -> dict:
    """Max land price P such that the (levered if debt on) flows meet IRR >= target AND multiple >= min.
    Feasibility falls as P rises, so we bisect. Returns P, equity flows at P and which hurdle binds."""
    def check(P):
        res = debt_mod.apply(flows_fn(P), dev_costs, debt)
        s = summarize(res["equity"])
        irr_ok = s["irr"] is not None and s["irr"] >= target_irr - 1e-9
        mult_ok = min_multiple is None or (s["multiple"] or 0) >= min_multiple - 1e-9
        return irr_ok and mult_ok, irr_ok, mult_ok, res, s
    base = solve_land_price(flows_fn, target_irr)
    scale = max(abs(base), 1.0) * 2 + 1e6
    lo, hi = 0.0, scale
    if not check(lo)[0] and min_multiple:
        r = solve_with_hurdles(flows_fn, dev_costs, debt, target_irr, None)
        r["binding"] = "IRR (2.0x multiple not reachable even with free land)"
        r["multiple_reached"] = False
        return r
    if not check(lo)[0]:
        # the project does not reach the hurdles even with free land: walk down until it does
        step, lo, found = scale / 8, 0.0, False
        for _ in range(40):
            hi, lo = lo, lo - step
            c = check(lo)
            if c[0]:
                found = True; break
            if c[4]["irr"] is None:
                break
        if not found:
            res = debt_mod.apply(flows_fn(base), dev_costs, debt)
            return dict(P=base, binding="IRR (unlevered fallback)", equity=res["equity"],
                        summary=summarize(res["equity"]), debt={k: v for k, v in res.items() if k != "equity"})
    else:
        while check(hi)[0]:
            hi *= 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if check(mid)[0]:
            lo = mid
        else:
            hi = mid
    ok, irr_ok, mult_ok, res, s = check(lo)
    _, irr_hi, mult_hi, _, _ = check(hi)
    binding = "equity multiple" if (min_multiple and irr_hi and not mult_hi) else "IRR"
    return dict(P=lo, binding=binding, equity=res["equity"], summary=s,
                debt={k: v for k, v in res.items() if k != "equity"})
