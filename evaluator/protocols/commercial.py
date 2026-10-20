"""Commercial & services (ficha v1, Founder 2026-10-19). Demand first, product second. Develop to rent.

Approval: the investor's own target IRR (20% pre-tax is the development reference, not a universal floor).
The required return is adjusted to risk (tenant, contract, speculative vs. pre-let, location, liquidity), but
never by automatic percentages: the risk factors are reported with their evidence and the investor decides.
A user counts as identified only with a BINDING letter of intent signed before paying for the land; otherwise
the deal is treated as speculative. Exit: (1) sell the stabilized asset (standard cap 12%, lower for AAA /
institutional buyers), (2) sell rental units to small investors, (3) hold and exit by either route at the end."""
from __future__ import annotations
import math
from ..cashflow import add, spread
from ..criteria import CONTINGENCY_PER_BLOCK, TARGET_IRR_PRETAX
from ..land import land_flows
from .base import solve_with_hurdles

COMMERCIAL_STANDARD_EXIT_CAP = 0.12   # CONFIRMED (Founder): standard exit cap, depends on size and segment
DEFAULTS = dict(sellable_efficiency=0.80, predevelopment_months=8, construction_months=14,
                avg_unit_m2=120, leases_per_month=None, rampup_months=12, stabilized_occupancy=0.95,
                opex_pct_of_rent=0.12, leasing_cost_months=2, collection_loss=0.04,
                months_after_stabilization=1, user_identified=False, loi_binding=False, committed_cap=None,
                exit_cap=None, speculative_exit_cap=COMMERCIAL_STANDARD_EXIT_CAP, sale_cost_pct=0.02,
                soft_pct_of_hard=0.12, contingency=CONTINGENCY_PER_BLOCK, target_yield_on_cost=0.12,
                target_irr=TARGET_IRR_PRETAX, exit_route="stabilized_sale",
                unit_sale_cap=None, unit_sale_months=12, unit_sale_cost_pct=0.05,
                hold_years=10, rent_growth=0.04)
EXIT_ROUTES = ("stabilized_sale", "unit_sale", "hold")


def user_status(p: dict) -> tuple[bool, str]:
    """Identified user = binding LOI signed before paying for the land (Founder)."""
    if p.get("user_identified") and p.get("loi_binding"):
        return True, "identified user with a binding letter of intent"
    if p.get("user_identified"):
        return False, "user in talks but no binding LOI: treated as speculative"
    return False, "no identified user: speculative development"


def exit_cap(p: dict) -> tuple[float, str]:
    identified, _ = user_status(p)
    if identified and p.get("committed_cap"):
        return p["committed_cap"], "cap agreed with the identified user / buyer"
    if p.get("exit_cap"):
        return p["exit_cap"], "exit cap given (size and segment)"
    return p["speculative_exit_cap"], "standard commercial exit cap"


def risk_factors(p: dict) -> list[dict]:
    """Evidence that raises or lowers the required return. Reported, never converted into automatic %."""
    out = []
    identified, ustat = user_status(p)
    out.append(dict(factor="Pre-let status", direction="lower" if identified else "higher", evidence=ustat))
    if p.get("tenant_rating"):
        aaa = str(p["tenant_rating"]).upper() == "AAA"
        out.append(dict(factor="Tenant credit", direction="lower" if aaa else "higher",
                        evidence=f"tenant rated {p['tenant_rating']}"))
    if p.get("lease_years"):
        out.append(dict(factor="Lease term", direction="lower" if p["lease_years"] >= 10 else "higher",
                        evidence=f"{p['lease_years']}-year mandatory term"))
    if p.get("securitizable_lease"):
        out.append(dict(factor="Lease designed to securitize the rents", direction="lower",
                        evidence="rent locked in under a securitizable contract"))
    if p.get("location_exceptional"):
        out.append(dict(factor="Hard-to-replicate location", direction="lower",
                        evidence="exceptional location: patrimonial value and appreciation"))
    if p.get("zone_vacancy") is not None:
        v = p["zone_vacancy"]
        out.append(dict(factor="Competing vacancy", direction="higher" if v > 0.10 else "neutral",
                        evidence=f"{v:.0%} vacancy in comparable centres nearby"))
    return out


def build(p: dict):
    p = {**DEFAULTS, **p}
    if p["exit_route"] not in EXIT_ROUTES:
        raise ValueError(f"exit_route must be one of {EXIT_ROUTES}")
    gla = p.get("gla_m2") or p["land_area_m2"] * p["far"] * p["sellable_efficiency"]
    built = gla / p["sellable_efficiency"]
    units = max(1, math.floor(gla / p["avg_unit_m2"]))
    stab = units * p["stabilized_occupancy"]
    rampup = math.ceil(stab / p["leases_per_month"]) if p.get("leases_per_month") else p["rampup_months"]
    start_c = p["predevelopment_months"]; end_c = start_c + p["construction_months"]
    stab_m = end_c + rampup
    route = p["exit_route"]
    if route == "hold":
        sale_m = stab_m + int(p["hold_years"] * 12)
    else:
        sale_m = stab_m + p["months_after_stabilization"]
    unit_months = p["unit_sale_months"] if route == "unit_sale" else 0
    horizon = sale_m + unit_months + 1
    hard_t = built * p["hard_cost_m2"] * (1 + p["contingency"])
    soft_t = built * p["hard_cost_m2"] * p["soft_pct_of_hard"] * (1 + p["contingency"])
    hard_series = spread(-hard_t, start_c, p["construction_months"], horizon)   # bridge-loan base (Founder)
    dev = add(hard_series, spread(-soft_t, 0, end_c, horizon))
    full_rent_m = gla * p["rent_m2_month"]
    margin = (1 - p["collection_loss"]) * (1 - p["opex_pct_of_rent"])
    stab_noi_y = full_rent_m * 12 * p["stabilized_occupancy"] * margin
    cap, cap_src = exit_cap(p)
    g = (1 + p["rent_growth"]) ** (1 / 12) - 1 if route == "hold" else 0.0
    noi = [0.0] * horizon
    sold_share = 0.0
    for t in range(end_c, horizon):
        k = t - end_c
        occ = p["stabilized_occupancy"] * min(1.0, (k + 1) / max(1, rampup))
        growth = (1 + g) ** max(0, t - stab_m)
        if route == "unit_sale" and t > sale_m:
            sold_share = min(1.0, (t - sale_m) / unit_months)
        if t > sale_m and route != "unit_sale":
            break
        noi[t] = full_rent_m * occ * margin * growth * (1 - sold_share)
        if k < rampup:
            noi[t] -= full_rent_m * p["stabilized_occupancy"] / max(1, rampup) * p["leasing_cost_months"]
    if route == "unit_sale":
        ucap = p.get("unit_sale_cap") or cap
        total = stab_noi_y / ucap * (1 - p["unit_sale_cost_pct"])
        for t in range(sale_m + 1, sale_m + unit_months + 1):
            noi[t] += total / unit_months
        exit_value, exit_src = stab_noi_y / ucap, f"units sold to small investors at {ucap:.1%} cap over {unit_months} months"
    else:
        grown = stab_noi_y * ((1 + g) ** (sale_m - stab_m))
        exit_value = grown / cap
        noi[sale_m] += exit_value * (1 - p["sale_cost_pct"])
        exit_src = cap_src if route == "stabilized_sale" else f"held {p['hold_years']} years, then sold ({cap_src})"
    flows = add(dev, noi)
    structure = p.get("land_structure", {"upfront_pct": 1.0, "deferred": []})

    def flows_lin(P):
        return add(flows, land_flows(P, structure, horizon))
    bd = dict(gla_m2=gla, built_m2=built, units=units, lease_up_months=rampup, sale_month=sale_m,
              hard_with_contingency=hard_t, soft_with_contingency=soft_t, stabilized_noi_year=stab_noi_y,
              noi_margin=margin, exit_cap=cap, exit_cap_source=exit_src, exit_value=exit_value,
              exit_route=route, horizon_months=horizon)
    return flows_lin, bd, hard_series, p


def evaluate(p: dict) -> dict:
    flows_lin, bd, hard_series, pp = build(p)
    from ..debt import DEFAULT_DEBT
    debt = {**DEFAULT_DEBT, **(p.get("debt") or {})}
    debt.setdefault("cap_amount", debt["max_pct_of_sales"] * bd["exit_value"])
    target = pp["target_irr"]
    sol = solve_with_hurdles(flows_lin, hard_series, debt, target_irr=target, min_multiple=None)
    P = sol["P"]
    total_cost = P + bd["hard_with_contingency"] + bd["soft_with_contingency"]
    yoc = bd["stabilized_noi_year"] / total_cost if total_cost > 0 else None
    tyoc = pp["target_yield_on_cost"]
    identified, ustat = user_status(pp)
    return dict(supported_land_value=P, binding_hurdle=sol["binding"], equity_metrics=sol["summary"],
                financing=sol["debt"], target_irr=target, yield_on_cost=yoc, target_yield_on_cost=tyoc,
                meets_target_yield=(yoc is not None and yoc >= tyoc - 1e-9),
                land_at_target_yield=bd["stabilized_noi_year"] / tyoc - bd["hard_with_contingency"] - bd["soft_with_contingency"],
                exit_cap=bd["exit_cap"], development_spread=(yoc - bd["exit_cap"]) if yoc is not None else None,
                user_identified=identified, user_status=ustat, risk_factors=risk_factors(pp),
                note=("The investor's target IRR approves (20% pre-tax is the development reference). Risk factors are "
                      "evidence, not automatic adjustments. Only a binding LOI makes the user 'identified'."),
                breakdown=bd, flows_at_supported=sol["equity"])
