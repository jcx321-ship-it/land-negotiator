"""Investment memo. Numbers always come from the engine; an LLM may only add a narrative."""
from __future__ import annotations

T = {
 "en": dict(title="Land Offer Memo", verdict="Verdict", why="Why", gates="Stage 0 gates", value="Value",
            A="A · supported by the project", B="B · closed land comparables", max="Maximum bid (lower of A and B)",
            ask="Asking price", scen="Market scenarios (negotiation space)", struct="Payment structure", dest="Destination",
            pending="Pending due diligence", metrics="Project metrics at the maximum bid", demo="FICTITIOUS DATA - demo only",
            protocol="Protocol", note="Analyst note"),
 "es": dict(title="Memo de oferta de terreno", verdict="Dictamen", why="Por qué", gates="Filtros etapa 0", value="Valor",
            A="A · soportado por el proyecto", B="B · comparables cerrados de tierra", max="Oferta máxima (el menor de A y B)",
            ask="Precio pedido", scen="Escenarios de mercado (espacio de negociación)", struct="Estructura de pago", dest="Destino",
            pending="Due diligence pendiente", metrics="Métricas del proyecto a la oferta máxima", demo="DATOS FICTICIOS - sólo demo",
            protocol="Protocolo", note="Nota del analista"),
}


def _m(x):
    return "n/a" if x is None else f"{x:,.0f}"


def render(r: dict, lang: str = "en", narrative: str | None = None) -> str:
    L = T[lang]
    out = [f"# {L['title']} - {r['case_id']}", f"_{L['demo']}: {r.get('label','')}_", "",
           f"## {L['verdict']}: **{r['verdict']}**  ·  {r['vocation']}", "", f"### {L['why']}",
           *[f"- {x}" for x in r.get("reasons", [])], ""]
    tf = r.get("thesis_fit") or {}
    if tf.get("applied"):
        out += [f"### Thesis fit ({tf.get('thesis_id')}): {'fits' if tf['fits'] else 'does NOT fit'}",
                *[f"- {'OK' if c['ok'] else 'NO'} · {c['label']}" for c in tf["checks"]], ""]
    if r["verdict"] == "NO FIT":
        return "\n".join(out) + "\n"
    g = r["gates"]
    out += [f"### {L['gates']}: {g['status']}", *[f"- {x}" for x in g["kill_land"] + g["kill_vocation"] + g["open_risks"]]]
    if "protocol" in r:
        p = r["protocol"]
        out += ["", f"### {L['protocol']}: {p['status']}", *[f"{i+1}. {s}" for i, s in enumerate(p["steps"])]]
    else:
        m = r["metrics_at_supported"]
        out += ["", f"### {L['value']}", "| | MXN |", "|---|---:|",
                f"| {L['A']} | {_m(r['value_A_project'])} |", f"| {L['B']} | {_m(r['value_B_comparables'])} |",
                f"| **{L['max']}** | **{_m(r['max_bid'])}** |", f"| {L['ask']} | {_m(r['asking_price'])} |", "",
                f"Target: {r['target_irr']:.0%} IRR before taxes ({r['irr_basis']})" + ("; for sale also 2.0x equity multiple with debt." if r['vocation'] == 'residential_sale' else "."), *[f"- {n}" for n in r["comparables_notes"]]]
        if r["scenarios"]:
            out += ["", f"### {L['scen']}", "| Scenario | Evidence | Max bid |", "|---|---|---:|",
                    *[f"| {s['name']} | {s['evidence']} | {_m(s['max_bid'])} |" for s in r["scenarios"]]]
        pr = r["protocol_result"]
        if "structure_value" in pr:
            out += ["", f"### {L['struct']}", f"- Supported with the proposed structure: {_m(pr['supported_land_value'])} (cash {_m(pr['supported_cash_part'])} + in kind {_m(pr['in_kind_value'])})",
                    f"- Supported if paid 100% cash upfront: {_m(pr['supported_if_paid_cash_upfront'])}",
                    f"- Value created by deferral / in kind: {_m(pr['structure_value'])}"]
        if "yield_on_cost" in pr:
            bd = pr["breakdown"]
            out += ["", f"- Yield on total cost {pr['yield_on_cost']:.1%} (target {pr['target_yield_on_cost']:.0%}) vs exit cap {pr['exit_cap']:.1%} ({bd['exit_cap_source']}); spread {pr['development_spread']:.1%}.",
                    f"- Lease-up {bd['lease_up_months']} months (market absorption), sale at month {bd['sale_month']}. Land that would deliver exactly {pr['target_yield_on_cost']:.0%}: {_m(pr['land_at_target_yield'])}.",
                    f"- {pr['note']}"]
        if pr.get("risk_factors"):
            out += ["", "### Risk factors (evidence, not automatic adjustments)",
                    *[f"- {x['factor']}: required return {x['direction']} · {x['evidence']}" for x in pr["risk_factors"]],
                    f"- Exit route: {pr['breakdown']['exit_route']} ({pr['breakdown']['exit_cap_source']}). Target IRR {pr['target_irr']:.0%} (investor's)."]
        fin = pr.get("financing") or {}
        if fin.get("enabled"):
            out += [f"- Financing on: {fin['ltc']:.0%} of {fin.get('base', 'hard construction costs')} at {fin['rate']:.1%}, peak debt {_m(fin['peak_debt'])}, interest {_m(fin['interest'])}. Binding hurdle: {pr.get('binding_hurdle')}."]
        out += ["", f"### {L['metrics']}", f"- Equity IRR {m['irr']:.1%} · equity multiple {m['multiple']:.2f}x · peak equity {_m(m['peak_equity'])}"]
        if r.get("quick_tests"):
            qt = r["quick_tests"]
            if "land_to_revenue_at_asking" in qt:
                q = qt["land_to_revenue_at_asking"]
                out += [f"- Quick test land/revenue at asking: {q['ratio']:.1%} ({q['band']}). {q['note']}"]
            if "hard_cost_to_sales" in qt:
                q = qt["hard_cost_to_sales"]
                out += [f"- Quick test hard costs/sales: {q['ratio']:.1%} vs standard {q['standard']:.0%} ({q['band']})."]
            if "proforma_at_max_bid" in qt:
                sh = qt["proforma_at_max_bid"]["shares"]; st = qt["proforma_at_max_bid"]["standard"]
                out += ["- Pro forma at max bid (% of sales, standard in brackets): " + " · ".join(
                    f"{k.replace('_', ' ')} {sh[k]:.1%} [{st[k]:.0%}]" for k in st)]
    if r.get("destination"):
        out += ["", f"### {L['dest']}", f"- {r['destination']}"]
    if g["pending"]:
        out += ["", f"### {L['pending']}", *[f"- {x}" for x in g["pending"]]]
    if narrative:
        out += ["", f"### {L['note']}", narrative.strip()]
    return "\n".join(out) + "\n"
