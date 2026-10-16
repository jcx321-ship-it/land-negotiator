"""Vocations whose protocol is only partly reconstructed from the Founder's evidence. They return the
checklist the evidence supports and refuse to invent a price."""
from __future__ import annotations

PARTIAL = {
    "land_banking": dict(
        status="PARTIAL PROTOCOL - no automatic price",
        steps=["Read the city: historical growth and direction of the urban footprint; is the urban area under pressure (prices up, people no longer fit)?",
               "Identify change drivers: announced investment, roads, rail, energy, anchor projects; current state -> drivers -> possible future state.",
               "Read economic corridors and their stage, not just distance to the centre.",
               "Normative path as value creation (urban development plan, partial plan, master plan) - underwrite on CURRENT use; the change is upside.",
               "Gross -> cessions/infrastructure -> usable -> monetizable land before any value per m2.",
               "Cost floor per m2 (land + accumulated holding costs: trust, legal, management) vs. today's sale value.",
               "Title regularisation and hectare reconciliation as the dominant risk; pay against milestones."],
        evidence="Large-tract land-banking files and a commissioned territorial intelligence study (2019)."),
    "carbon": dict(
        status="PARTIAL PROTOCOL - no own method to measure carbon capture",
        steps=["Tenure path (e.g. communal/ejido land) with payments tied to delivered milestones.",
               "Value = carbon-credit income (ha x credits/ha x price, growth, insurance/provision) + land sale at horizon.",
               "Control metric: purchase $/m2 = peak capital required / m2.",
               "Capture, baseline and additionality require a third-party methodology: no Founder criterion exists."],
        evidence="One 2022 carbon-land model (authorship not verified)."),
    "agricultural": dict(
        status="NO PROTOCOL - no own evidence",
        steps=["The Founder's stated principle: vocation from soil, water and climate; do not force crops foreign to the land.",
               "Valuation method for productive land not documented: do not price automatically."],
        evidence="Only third-party analyses and AI-generated drafts; none is the Founder's criterion."),
}


def evaluate(vocation: str) -> dict:
    return PARTIAL[vocation]
