"""Industrial lots / park. Evidence: past industrial lot models (net area varies 44-85% with rail, gas-duct and
road afectaciones; product by lot type with very different absorption; land often contributed with a floor price)."""
from __future__ import annotations
import math
from ..cashflow import add, spread
from ..criteria import CONTINGENCY_PER_BLOCK
from ..land import land_flows
from .base import solve_land_price

DEFAULTS = dict(predevelopment_months=10, urbanization_months=14, sales_start_month=10,
                soft_pct_of_hard=0.15, commission_pct=0.07, contingency=CONTINGENCY_PER_BLOCK)


def build(p: dict):
    p = {**DEFAULTS, **p}
    gross = p["gross_m2"]
    net = gross * p["net_pct"]
    start_u = p["predevelopment_months"]
    lots = p["lot_types"]  # [{name, share_of_net, price_m2, absorption_m2_month}]
    sell_end = max(p["sales_start_month"] + math.ceil(net * l["share_of_net"] / l["absorption_m2_month"]) for l in lots)
    horizon = max(start_u + p["urbanization_months"], sell_end) + 2
    rev = [0.0] * horizon
    for l in lots:
        area = net * l["share_of_net"]; m = p["sales_start_month"]; left = area
        while left > 1e-6:
            a = min(l["absorption_m2_month"], left)
            rev[m] += a * l["price_m2"]; left -= a; m += 1
    urb = gross * p["urbanization_cost_per_gross_m2"] * (1 + p["contingency"])
    infra = sum(x["cost"] for x in p.get("infrastructure", [])) * (1 + p["contingency"])
    soft = (urb + infra) / (1 + p["contingency"]) * p["soft_pct_of_hard"] * (1 + p["contingency"])
    flows = add(rev, [-x * p["commission_pct"] for x in rev],
                spread(-urb, start_u, p["urbanization_months"], horizon),
                spread(-infra, start_u, p["urbanization_months"], horizon),
                spread(-soft, 0, start_u + p["urbanization_months"], horizon))
    structure = p.get("land_structure", {"upfront_pct": 1.0, "deferred": []})
    def flows_lin(P):
        return add(flows, land_flows(P, structure, horizon))
    open_infra = [x["name"] for x in p.get("infrastructure", []) if x.get("status") in (None, "open")]
    bd = dict(gross_m2=gross, net_m2=net, net_pct=p["net_pct"], revenue=sum(rev), urbanization=urb,
              infrastructure=infra, open_infrastructure=open_infra, horizon_months=horizon)
    return flows_lin, bd


def evaluate(p: dict) -> dict:
    flows_lin, bd = build(p)
    P = solve_land_price(flows_lin)
    return dict(supported_land_value=P, supported_per_gross_m2=P / bd["gross_m2"],
                land_to_revenue_at_supported=P / bd["revenue"] if bd["revenue"] else None,
                breakdown=bd, flows_at_supported=flows_lin(P))
