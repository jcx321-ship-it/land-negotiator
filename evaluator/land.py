"""How the land is paid: upfront, deferred, in kind. The Founder defers and pays in kind as much as possible."""
from __future__ import annotations


def land_flows(price: float, structure: dict, horizon: int, in_kind_value: float = 0.0) -> list[float]:
    """Cash outflows for the land. price = total agreed land price (cash + in kind).
    structure: {"upfront_pct": 0.3, "deferred": [{"month": 12, "pct": 0.7}], "acq_cost_pct": 0.06}
    pcts apply to the CASH portion (price - in_kind_value). Acquisition costs are paid at month 0 on the full price."""
    cash = price - in_kind_value
    out = [0.0] * horizon
    up = structure.get("upfront_pct", 1.0)
    out[0] -= cash * up
    rest = 1.0 - up
    for d in structure.get("deferred", []):
        m = min(int(d["month"]), horizon - 1)
        out[m] -= cash * d["pct"]
        rest -= d["pct"]
    if abs(rest) > 1e-6:
        raise ValueError("land payment percentages must add up to 100%")
    out[0] -= price * structure.get("acq_cost_pct", 0.0)
    return out


CONTADO = {"upfront_pct": 1.0, "deferred": []}
