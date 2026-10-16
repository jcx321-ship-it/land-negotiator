"""Residential for sale (Habitacional ficha v1). Zoning first, market validates price and pace. Pre-tax.
Approval: 20% equity IRR AND 2.0x equity multiple, with the financing switch on by default."""
from __future__ import annotations
import math
from ..cashflow import add, spread
from ..criteria import CONTINGENCY_PER_BLOCK
from ..land import land_flows
from .base import solve_with_hurdles
from ..criteria import MIN_EQUITY_MULTIPLE

# HYPOTHESIS figures (MXN/m2 built), pending the Founder's ranges. Cost depends on specification, mainly
# finishes, not on the segment (Founder, 2026-10-06).
STRUCTURE_COST_M2 = {"low_rise": 7500, "mid_rise": 8500, "high_rise": 10500, "houses": 7000}
FINISH_COST_M2 = {"basic": 3000, "medium": 4500, "high": 6500, "luxury": 9500}


def hard_cost_m2(p: dict) -> float:
    if p.get("hard_cost_m2"):
        return p["hard_cost_m2"]
    return (STRUCTURE_COST_M2[p.get("structure", "mid_rise")] + FINISH_COST_M2[p.get("finish_level", "medium")]
            + p.get("amenities_cost_m2", 1500))

DEFAULTS = dict(sellable_efficiency=0.82, avg_unit_m2=90, predevelopment_months=8, construction_months=20,
                absorption_units_month=3, down_pct=0.10, during_pct=0.10, soft_pct_of_hard=0.12,
                marketing_pct=0.02, commission_pct=0.04, contingency=CONTINGENCY_PER_BLOCK, in_kind_units=0)


def build(p: dict):
    p = {**DEFAULTS, **p}
    built = p["land_area_m2"] * p["far"]
    units = math.floor(built * p["sellable_efficiency"] / p["avg_unit_m2"])
    unit_price = p["avg_unit_m2"] * p["sale_price_m2"]
    special = unit_price * (1 - p["commission_pct"])          # in-kind price passes on the saved commission
    k = int(p["in_kind_units"]); units_for_sale = units - k
    start_c = p["predevelopment_months"]; end_c = start_c + p["construction_months"]
    sell_months = math.ceil(units_for_sale / p["absorption_units_month"])
    horizon = max(end_c, start_c + sell_months) + 3
    rev = [0.0] * horizon
    sold = 0; m = start_c
    while sold < units_for_sale:
        n = min(p["absorption_units_month"], units_for_sale - sold)
        cash = n * unit_price
        rev[m] += cash * p["down_pct"]
        span = max(0, end_c - m - 1)
        if span:
            for t in range(m + 1, end_c):
                rev[t] += cash * p["during_pct"] / span
            rev[max(end_c, m + 1)] += cash * (1 - p["down_pct"] - p["during_pct"])
        else:
            rev[max(end_c, m + 1)] += cash * (1 - p["down_pct"])
        sold += n; m += 1
    hcm2 = hard_cost_m2(p)
    hard = built * hcm2
    hard_t = hard * (1 + p["contingency"])                     # contingency by block
    soft = hard * p["soft_pct_of_hard"]
    soft_t = soft * (1 + p["contingency"])
    gross_rev = units_for_sale * unit_price
    var = gross_rev * (p["marketing_pct"] + p["commission_pct"])
    hard_series = spread(-hard_t, start_c, p["construction_months"], horizon)   # bridge-loan base (Founder)
    dev = add(hard_series,
              spread(-soft_t * 0.6, 0, max(1, start_c), horizon),
              spread(-soft_t * 0.4, start_c, p["construction_months"], horizon))
    costs = add(dev, [-x * (p["marketing_pct"] + p["commission_pct"]) for x in rev])
    in_kind_value = k * special
    structure = p.get("land_structure", {"upfront_pct": 1.0, "deferred": []})

    def flows_lin(P):  # linear in P for solving (in-kind fixed value inside P)
        lf = land_flows(P + in_kind_value, structure, horizon, in_kind_value)
        return add(rev, costs, lf)
    breakdown = dict(built_m2=built, units=units, units_for_sale=units_for_sale, in_kind_units=k,
                     unit_price=unit_price, special_unit_price=special, gross_revenue=gross_rev,
                     total_revenue_equiv=units * unit_price, hard_with_contingency=hard_t,
                     soft_with_contingency=soft_t, variable_costs=var, horizon_months=horizon, hard_cost_m2=hcm2)
    return flows_lin, breakdown, in_kind_value, hard_series


def evaluate(p: dict) -> dict:
    flows_lin, bd, in_kind, dev = build(p)
    from ..debt import DEFAULT_DEBT
    debt = {**DEFAULT_DEBT, **(p.get("debt") or {})}
    debt.setdefault("cap_amount", debt["max_pct_of_sales"] * bd["gross_revenue"])
    levered = (debt or {}).get("enabled", True)
    mm = p.get("min_multiple", MIN_EQUITY_MULTIPLE) if levered else None   # 2.0x is measured with debt (Founder)
    sol = solve_with_hurdles(flows_lin, dev, debt, min_multiple=mm)
    cash_part = sol["P"]
    supported_total = cash_part + in_kind
    p_contado = {**p, "land_structure": {"upfront_pct": 1.0, "deferred": [], "acq_cost_pct": p.get("land_structure", {}).get("acq_cost_pct", 0.0)}, "in_kind_units": 0}
    fl_c, _, _, dev_c = build(p_contado)
    contado = solve_with_hurdles(fl_c, dev_c, debt, min_multiple=mm)["P"]
    rev_eq = bd["total_revenue_equiv"]
    return dict(supported_land_value=supported_total, supported_cash_part=cash_part, in_kind_value=in_kind,
                supported_if_paid_cash_upfront=contado, structure_value=supported_total - contado,
                land_to_revenue_at_supported=supported_total / rev_eq if rev_eq else None,
                binding_hurdle=sol["binding"], multiple_reached=sol.get("multiple_reached", True), min_multiple=mm, equity_metrics=sol["summary"], financing=sol["debt"],
                breakdown=bd, flows_at_supported=sol["equity"])
