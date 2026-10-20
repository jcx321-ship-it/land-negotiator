"""Developer thesis (Founder, 2026-10-06): the primary user is a developer with a defined investment line.
Vocation and segment are captured once as a thesis; every offer is first checked against it, and an offer that
does not fit is discarded before any number is run."""
from __future__ import annotations


def fit(offer: dict, thesis: dict | None) -> dict:
    if not thesis:
        return dict(fits=True, checks=[], applied=False)
    area = (offer.get("params") or {}).get("land_area_m2") or (offer.get("params") or {}).get("gross_m2")
    checks = []
    def chk(ok, label):
        checks.append(dict(ok=bool(ok), label=label))
    chk(offer.get("vocation") == thesis["vocation"], f"Vocation {offer.get('vocation')} vs thesis {thesis['vocation']}")
    if thesis.get("markets"):
        chk(offer.get("market") in thesis["markets"], f"Market {offer.get('market')} vs {', '.join(thesis['markets'])}")
    if thesis.get("land_m2") and area:
        lo, hi = thesis["land_m2"]
        chk(lo <= area <= hi, f"Land {area:,.0f} m2 vs range {lo:,.0f}-{hi:,.0f} m2")
    if thesis.get("max_land_ticket") and offer.get("asking_price"):
        chk(offer["asking_price"] <= thesis["max_land_ticket"], f"Ticket {offer['asking_price']:,.0f} vs max {thesis['max_land_ticket']:,.0f}")
    # line-of-business requirements come from the developer, who knows his format (Founder, 2026-10-19)
    missing = []
    params = offer.get("params") or {}
    for key, req in (thesis.get("requirements") or {}).items():
        field, op = (key[4:], "min") if key.startswith("min_") else ((key[4:], "max") if key.startswith("max_") else (key, "eq"))
        val = params.get(field, offer.get(field))
        if val is None:
            missing.append(f"Format requirement not evidenced yet: {field} ({op} {req}).")
            continue
        ok = val >= req if op == "min" else (val <= req if op == "max" else val == req)
        chk(ok, f"{field} {val:,} vs {op} {req:,}" if isinstance(val, (int, float)) else f"{field} {val} vs {req}")
    return dict(fits=all(c["ok"] for c in checks), checks=checks, applied=True, thesis_id=thesis.get("developer_id"),
                missing_evidence=missing)


def apply_product(offer: dict, thesis: dict | None) -> dict:
    """Thesis product defaults (segment, finishes, unit size, absorption, debt) fill what the offer leaves blank."""
    if not thesis or not thesis.get("product"):
        return offer
    params = {**thesis["product"], **offer.get("params", {})}
    return {**offer, "params": params}
