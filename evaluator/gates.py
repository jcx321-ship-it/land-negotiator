"""Stage 0 gates: universal kill criteria and open risks (Founder doctrine)."""
from __future__ import annotations


def run_gates(dd: dict) -> dict:
    """dd keys (True/False/None=unknown):
    title_certain, seller_can_transfer, social_opposition_material, protected_area_incompatible,
    nonremediable_physical, current_zoning_allows_product, market_absorbs,
    critical_feasibility: 'accredited' | 'prefeasibility' | 'open' | 'not_viable' | None
    """
    kill_land, kill_vocation, open_risks, pending = [], [], [], []
    def unknown(k, label):
        if dd.get(k) is None:
            pending.append(label)
    if dd.get("title_certain") is False or dd.get("seller_can_transfer") is False:
        kill_land.append("No certainty of title or of the seller's power to transfer.")
    unknown("title_certain", "Title certainty not yet established by DD.")
    unknown("seller_can_transfer", "Seller's power to transfer not yet established.")
    if dd.get("social_opposition_material") is True:
        kill_land.append("Material community opposition able to stop execution.")
    unknown("social_opposition_material", "Social DD of the surroundings not done.")
    if dd.get("protected_area_incompatible") is True:
        kill_vocation.append("Protected natural area incompatible with this product.")
    if dd.get("nonremediable_physical") is True:
        kill_vocation.append("Non-remediable physical condition (e.g. severe flood risk) for this product.")
    if dd.get("current_zoning_allows_product") is False:
        kill_vocation.append("Current zoning does not allow this product; future rezoning is upside, not paid today.")
    unknown("current_zoning_allows_product", "Current land-use certificate not verified.")
    if dd.get("market_absorbs") is False:
        kill_vocation.append("No market: comparable product nearby is stalled, so this product is discarded (slow is fine, stalled is not).")
    feas = dd.get("critical_feasibility")
    if feas == "not_viable":
        kill_vocation.append("A critical feasibility (energy, water, access) has no viable solution for this product.")
    elif feas == "open":
        open_risks.append("Critical feasibility still open: structure the deal so capital is not exposed until it is accredited.")
    elif feas is None:
        pending.append("Critical feasibilities not reviewed.")
    status = "NO-GO (land)" if kill_land else ("NO-GO (this vocation)" if kill_vocation else ("PASS - DD pending" if pending else "PASS"))
    return dict(status=status, kill_land=kill_land, kill_vocation=kill_vocation,
                open_risks=open_risks, pending=pending)
