"""Develop to rent (Habitacional ficha v1, Founder 2026-10-08). Value comes from rent and NOI.
Unified logic: aim at a 12% yield on total cost (NOI / investment incl. land), exit by selling the stabilized
building at the cap signed with a buyer (forward sale / binding LOI) or at a speculative 10% cap; the horizon is
given by market absorption (lease-up), and the 20% IRR is what approves the deal. Financing switch on by default.
Evidence for the NOI chain: achieved rent (not asking), real opex, collection loss, lease-up apart from operation."""
from __future__ import annotations
import math
from ..cashflow import add, spread
from ..criteria import CONTINGENCY_PER_BLOCK, RENTAL_TARGET_YIELD_ON_COST, RENTAL_SPECULATIVE_EXIT_CAP
from ..land import land_flows
from .base import solve_with_hurdles

DEFAULTS = dict(sellable_efficiency=0.85, predevelopment_months=8, construction_months=20,
                avg_unit_m2=70, leases_per_month=None, rampup_months=12,
                stabilized_occupancy=0.95, opex_pct_of_rent=0.30, leasing_cost_months=1, collection_loss=0.03,
                months_after_stabilization=1, forward_sale=False, committed_cap=None,
                speculative_exit_cap=RENTAL_SPECULATIVE_EXIT_CAP, sale_cost_pct=0.02, soft_pct_of_hard=0.12,
                contingency=CONTINGENCY_PER_BLOCK, target_yield_on_cost=RENTAL_TARGET_YIELD_ON_COST)


def exit_cap(p: dict) -> tuple[float, str]:
    if p.get("forward_sale") and p.get("committed_cap"):
        return p["committed_cap"], "signed buyer's cap (forward sale)"
    if p.get("exit_cap"):
        return p["exit_cap"], "exit cap given"
    return p["speculative_exit_cap"], "speculative exit (no signed buyer)"


def build(p: dict):
    p = {**DEFAULTS, **p}
    gla = p.get("gla_m2") or p["land_area_m2"] * p["far"] * p["sellable_efficiency"]
    built = gla / p["sellable_efficiency"]
    units = max(1, math.floor(gla / p["avg_unit_m2"]))
    stab_units = units * p["stabilized_occupancy"]
    rampup = math.ceil(stab_units / p["leases_per_month"]) if p.get("leases_per_month") else p["rampup_months"]
    start_c = p["predevelopment_months"]; end_c = start_c + p["construction_months"]
    sale_m = end_c + rampup + p["months_after_stabilization"]
    horizon = sale_m + 1
    hard_t = built * p["hard_cost_m2"] * (1 + p["contingency"])
    soft_t = built * p["hard_cost_m2"] * p["soft_pct_of_hard"] * (1 + p["contingency"])
    dev = add(spread(-hard_t, start_c, p["construction_months"], horizon), spread(-soft_t, 0, end_c, horizon))
    full_rent_m = gla * p["rent_m2_month"]
    noi = [0.0] * horizon
    for t in range(end_c, sale_m):
        k = t - end_c
        occ = p["stabilized_occupancy"] * min(1.0, (k + 1) / max(1, rampup))
        rent = full_rent_m * occ * (1 - p["collection_loss"])
        noi[t] = rent * (1 - p["opex_pct_of_rent"])
        if k < rampup:
            noi[t] -= full_rent_m * p["stabilized_occupancy"] / max(1, rampup) * p["leasing_cost_months"]
    stab_noi_y = full_rent_m * 12 * p["stabilized_occupancy"] * (1 - p["collection_loss"]) * (1 - p["opex_pct_of_rent"])
    cap, cap_src = exit_cap(p)
    exit_value = stab_noi_y / cap
    noi[sale_m] += exit_value * (1 - p["sale_cost_pct"])
    flows = add(dev, noi)
    structure = p.get("land_structure", {"upfront_pct": 1.0, "deferred": []})
    def flows_lin(P):
        return add(flows, land_flows(P, structure, horizon))
    bd = dict(gla_m2=gla, built_m2=built, units=units, lease_up_months=rampup, sale_month=sale_m,
              hard_with_contingency=hard_t, soft_with_contingency=soft_t, stabilized_noi_year=stab_noi_y,
              noi_margin=(1 - p["opex_pct_of_rent"]) * (1 - p["collection_loss"]),
              exit_cap=cap, exit_cap_source=cap_src, exit_value=exit_value, horizon_months=horizon)
    return flows_lin, bd, dev, p


def evaluate(p: dict) -> dict:
    flows_lin, bd, dev, pp = build(p)
    sol = solve_with_hurdles(flows_lin, dev, p.get("debt"), min_multiple=None)
    P = sol["P"]
    total_cost = P + bd["hard_with_contingency"] + bd["soft_with_contingency"]
    yoc = bd["stabilized_noi_year"] / total_cost if total_cost > 0 else None
    target = pp["target_yield_on_cost"]
    # land that would deliver exactly the 12% target yield on total cost (read alongside the IRR answer)
    land_at_target_yield = bd["stabilized_noi_year"] / target - bd["hard_with_contingency"] - bd["soft_with_contingency"]
    return dict(supported_land_value=P, binding_hurdle=sol["binding"], equity_metrics=sol["summary"],
                financing=sol["debt"], yield_on_cost=yoc, target_yield_on_cost=target,
                meets_target_yield=(yoc is not None and yoc >= target - 1e-9),
                land_at_target_yield=land_at_target_yield, exit_cap=bd["exit_cap"],
                development_spread=(yoc - bd["exit_cap"]) if yoc is not None else None,
                note="The 12% yield on cost is the development target, the exit cap is the mechanism, the 20% IRR approves (Founder).",
                breakdown=bd, flows_at_supported=sol["equity"])
