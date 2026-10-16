# SPEC - Land Negotiator v0.3

## Modules
- `criteria.py` - the buyer's rules with provenance (CONFIRMED / HISTORICAL / HYPOTHESIS) and constants (20% pre-tax IRR, 5% contingency per block, land/revenue bands).
- `gates.py` - stage 0: kills the land (title, transfer, community opposition) or the vocation (zoning, protected area, non-remediable condition, non-viable feasibility); open risks and pending DD.
- `thesis.py` - the developer's line (vocation, markets, land size range, max ticket); offers that do not fit are discarded before any number; thesis product defaults fill blanks.
- `debt.py` - financing switch: construction loan as % of development cost (land never financed), monthly capitalised interest, cash sweep; returns equity flows.
- `land.py` - land payment schedule: upfront %, deferred milestones, acquisition costs, in-kind portion.
- `protocols/` - one per vocation. Each builds monthly pre-tax project flows linear in the land price. Unlevered, the price that yields the target IRR is solved in closed form (NPV = 0); with financing on, `base.solve_with_hurdles` bisects for the highest land price that meets every hurdle (equity IRR, and for sale the 2.0x equity multiple) and reports which one binds.
  - `residential_sale` - hard cost from specification (structure + finishes + amenities); units from current FAR and efficiency; absorption; client payment scheme (down / during works / delivery); hard & soft with block contingency; marketing and commission; in-kind units removed from sales and valued at price net of commission.
  - `rental` - GLA and units; lease-up from market absorption (leases per month); collection loss, opex, leasing cost; sale at stabilization at the signed buyer's cap (forward sale) or a speculative 10%; 20% IRR approves; reports yield on cost vs the 12% target and the land that would deliver exactly 12%.
  - `industrial_lots` - gross -> net area, lot types with own price and absorption, urbanization per gross m2, infrastructure items with feasibility status.
  - `partial` - land banking and carbon (checklists from evidence), agricultural (no protocol). They never output a price.
- `engine.py` - gates -> protocol -> A (supported) and B (median of CLOSED comparables x area) -> max bid = min -> market scenarios -> verdict -> quick tests -> destination (irreplaceable -> rent; replaceable -> sell).
- `agent.py` / `llm.py` - Nemotron intake and red team via the OpenAI-compatible Token Factory API; JSON requested in the prompt and validated (JSON mode not tagged for Nemotron in the catalog).
- `webapi.py` - shared JSON API; `server.py` stdlib server; `api/*.py` the same endpoints as Vercel functions; daily AI cap.

## Verdict
NO FIT from the thesis. NO-GO (land) / NO-GO (this vocation) from gates. NO-GO if the 2.0x multiple cannot be reached even with free land. Else GO if asking <= max bid with no open critical risk;
BORDERLINE if it fits but a critical risk is open, or if it exceeds the base but a market scenario supports it;
NO-GO otherwise.

## Known simplifications
Pre-tax; simple construction loan (no permanent debt); industrial lots unlevered; linear construction spend; no inflation; single phase; comparables homologation is manual.
