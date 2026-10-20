"""Orchestrates the Founder's land criterion: gates -> protocol by vocation -> value A (supported by the
project) vs value B (closed comparables) -> max bid = lower -> verdict -> negotiation space -> destination."""
from __future__ import annotations
import copy, statistics
from .gates import run_gates
from . import thesis as thesis_mod
from .criteria import HARD_COST_TO_SALES_STANDARD, PROFORMA_STANDARD, TARGET_IRR_PRETAX, LAND_TO_REVENUE_BANDS, IRR_BASIS
from .protocols import residential_sale, rental, industrial_lots, partial, commercial
from .protocols.base import summarize

PRICED = {"residential_sale": residential_sale, "rental": rental, "industrial_lots": industrial_lots,
          "commercial": commercial}


def _deep_merge(a: dict, b: dict) -> dict:
    out = copy.deepcopy(a)
    for k, v in b.items():
        out[k] = _deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def comparables_value(comps: list[dict], area: float) -> tuple[float | None, list[str]]:
    notes = []
    closed = [c["price_m2"] for c in comps if c.get("closed")]
    asking = [c for c in comps if not c.get("closed")]
    if asking:
        notes.append(f"{len(asking)} asking-price comparable(s) ignored: only closed transactions count (hypothesis pending Founder confirmation).")
    if not closed:
        notes.append("No closed land comparables: value B unavailable; max bid rests on the project alone.")
        return None, notes
    return statistics.median(closed) * area, notes


def evaluate_offer(offer: dict, thesis: dict | None = None) -> dict:
    voc = offer["vocation"]
    fit = thesis_mod.fit(offer, thesis)
    offer = thesis_mod.apply_product(offer, thesis)
    gates = run_gates(offer.get("dd", {}), voc)
    gates["pending"] += fit.get("missing_evidence", [])
    if gates["pending"] and gates["status"] == "PASS":
        gates["status"] = "PASS - DD pending"
    out = dict(case_id=offer.get("case_id"), label=offer.get("label"), vocation=voc, market=offer.get("market"),
               thesis_fit=fit, gates=gates, target_irr=TARGET_IRR_PRETAX, irr_basis=IRR_BASIS,
               asking_price=offer.get("asking_price"))
    if not fit["fits"]:
        out.update(verdict="NO FIT", reasons=["The offer is outside the developer's investment thesis: discarded before any number is run."])
        return out
    if voc not in PRICED:
        out.update(protocol=partial.evaluate(voc), verdict="NO AUTOMATIC VERDICT",
                   reasons=["This vocation's protocol is not fully reconstructed from the Founder's evidence; no price is invented."])
        if gates["status"].startswith("NO-GO"):
            out["verdict"] = gates["status"]
        return out
    mod = PRICED[voc]
    params = offer["params"]
    res = mod.evaluate(params)
    A = res["supported_land_value"]
    area = params.get("land_area_m2") or params.get("gross_m2")
    B, comp_notes = comparables_value(offer.get("comparables", []), area)
    max_bid = min(A, B) if B is not None else A
    binding = "project (A)" if (B is None or A <= B) else "comparables (B)"
    # market scenarios -> negotiation space (Founder: sensitivities from market evidence, not fixed stress)
    scen = []
    for s in offer.get("scenarios", []):
        r = mod.evaluate(_deep_merge(params, s.get("overrides", {})))
        v = r["supported_land_value"]
        scen.append(dict(name=s["name"], evidence=s.get("evidence", ""), supported_land_value=v,
                         max_bid=min(v, B) if B is not None else v))
    asking = offer.get("asking_price")
    reasons = list(gates["kill_land"] + gates["kill_vocation"])
    if gates["status"].startswith("NO-GO"):
        verdict = gates["status"]
    elif res.get("multiple_reached") is False:
        verdict = "NO-GO"
        reasons.append("The project cannot return the 2.0x equity multiple even with free land (measured with debt).")
    elif asking is None:
        verdict = "NO ASKING PRICE"
    elif asking <= max_bid and not gates["open_risks"]:
        verdict = "GO"
        hurd = f"{res.get('target_irr', TARGET_IRR_PRETAX):.0%} pre-tax IRR" + (" (investor's target)" if res.get("target_irr", TARGET_IRR_PRETAX) != TARGET_IRR_PRETAX else "") + (" and 2.0x equity multiple" if res.get("min_multiple") else "")
        reasons.append(f"Asking price fits under the maximum bid ({binding} binds) at {hurd}.")
    elif asking <= max_bid:
        verdict = "BORDERLINE"
        reasons.append("Price fits, but a critical risk is open: tie payments to its accreditation before exposure.")
        reasons += gates["open_risks"]
    else:
        best = max([x["max_bid"] for x in scen] + [max_bid])
        gap = asking / max_bid - 1 if max_bid > 0 else float("inf")
        if asking <= best:
            verdict = "BORDERLINE"
            reasons.append(f"Asking exceeds the base maximum bid by {gap:.0%}; only the most favourable market scenario supports it: negotiate or restructure.")
            ok = [x["name"] for x in scen if x["max_bid"] >= asking]
            reasons.append("Supported only if: " + "; ".join(ok) + ". Do not pay the asking price before that is secured.")
        else:
            verdict = "NO-GO"
            reasons.append(f"Asking exceeds the maximum bid by {gap:.0%} and no market scenario supports it.")
    if gates["open_risks"] and verdict not in ("GO",) and gates["open_risks"][0] not in reasons:
        reasons += gates["open_risks"]
    if res.get("structure_value", 0) > 0 and not verdict.startswith("NO-GO (land"):
        reasons.append(f"Deferral / payment in kind adds {res['structure_value']:,.0f} of supportable land value vs. paying cash upfront.")
    if voc == "commercial" and not verdict.startswith("NO-GO (land"):
        reasons.append(f"User status: {res['user_status']}.")
    if voc in ("rental", "commercial") and asking and not verdict.startswith("NO-GO (land"):
        bd = res["breakdown"]
        y_ask = bd["stabilized_noi_year"] / (asking + bd["hard_with_contingency"] + bd["soft_with_contingency"])
        res["yield_on_cost_at_asking"] = y_ask
        tgt = res["target_yield_on_cost"]
        reasons.append(f"Yield on total cost at the asking price: {y_ask:.1%} vs the {tgt:.0%} development target"
                       + (" (meets it)." if y_ask >= tgt - 5e-4 else " (below it: the margin depends on the exit cap)."))
    fin = res.get("financing") or {}
    if fin.get("enabled"):
        reasons.append(f"Financing on: {fin['ltc']:.0%} of {fin.get('base', 'hard construction costs')} at {fin['rate']:.1%}; hurdle that binds: {res.get('binding_hurdle')}.")
    quick = {}
    if voc == "residential_sale" and asking:
        rev = res["breakdown"]["total_revenue_equiv"]
        ratio = asking / rev
        lo, hi = LAND_TO_REVENUE_BANDS["low"], LAND_TO_REVENUE_BANDS["high"]
        band = "low" if ratio <= lo[1] else ("reference" if ratio <= hi[0] else ("high" if ratio <= hi[1] else "above the observed range"))
        quick["land_to_revenue_at_asking"] = dict(ratio=ratio, band=band,
            note="Quick test only (Founder): admissible % rises in expensive high-demand areas, falls in cheap abundant product.")
    bd = res.get("breakdown") or {}
    sales = bd.get("total_revenue_equiv") or bd.get("exit_value")
    if sales and bd.get("hard_with_contingency"):
        hr = bd["hard_with_contingency"] / sales
        std = HARD_COST_TO_SALES_STANDARD
        quick["hard_cost_to_sales"] = dict(ratio=hr, standard=std,
            band="standard" if hr <= std + 0.05 else ("above standard" if hr <= std + 0.15 else "costly"),
            note="Quick test (Founder): standard hard costs are ~40% of the sales value. Above it, check the "
                 "specification or whether the sale price is too low for the product.")
    if voc == "residential_sale" and bd.get("total_revenue_equiv"):
        rev = bd["total_revenue_equiv"]; c = 1 + bd.get("contingency", 0.05)
        land = res["supported_land_value"]
        hard = bd["hard_with_contingency"] / c; soft = bd["soft_with_contingency"] / c
        cont = bd["hard_with_contingency"] + bd["soft_with_contingency"] - hard - soft
        fin_i = (res.get("financing") or {}).get("interest", 0.0)
        shares = dict(land=land, hard_costs=hard, soft_and_sales_costs=soft + bd["variable_costs"], finance=fin_i,
                      contingency_and_other=cont)
        shares = {k: v / rev for k, v in shares.items()}
        shares["margin"] = 1 - sum(shares.values())
        quick["proforma_at_max_bid"] = dict(shares=shares, standard=PROFORMA_STANDARD,
            note="Founder's reference: land 20 / hard 40 / soft+sales 10 / finance 5 / contingency 5 / margin 20 "
                 "(share of sales value). The margin is not the hurdle: the 20% IRR and 2.0x approve.")
    destination = None
    if offer.get("irreplaceable") is True:
        destination = "Irreplaceable / premium: evaluate keeping it as a rental asset (Founder rule)."
    elif offer.get("irreplaceable") is False:
        destination = "Replaceable: develop, sell and recycle capital (Founder rule)."
    out.update(protocol_result={k: v for k, v in res.items() if k != "flows_at_supported"},
               metrics_at_supported=summarize(res["flows_at_supported"]),
               value_A_project=A, value_B_comparables=B, comparables_notes=comp_notes,
               max_bid=max_bid, binding=binding, scenarios=scen, verdict=verdict, reasons=reasons,
               quick_tests=quick, destination=destination,
               open_risks=gates["open_risks"], pending_dd=gates["pending"])
    return out
