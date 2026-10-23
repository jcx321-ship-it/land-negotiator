# Land Negotiator

**How much to pay for land, and how to pay it.** Paste a broker's land offer. **NVIDIA Nemotron** (served on
**Nebius Token Factory**) reads it into a structured offer, then plays **red team**: it attacks the deal's weakest
assumption, writes the questions to ask the seller and proposes a payment structure that keeps capital safe.
Deterministic code, encoding a senior Mexican developer's 20-year criterion, computes the maximum bid. The AI argues;
it never sets the number or the verdict.

**Try it in 30 seconds:** open the [live demo](https://land-negotiator.vercel.app), case I is preloaded, press
**Evaluate** with "AI red team" on. English and Spanish.

> All demo data is **fictitious**: invented developers, numbers and parcels. No client data.

## Why this is different
Land tools usually ask "what is this land worth?". A developer asks: **"Which project can really be built
on this land, at what risk and return, and how much can I pay today to do it?"** The criterion was
extracted from a practitioner through structured interviews, checked against his historical project
models and against public references. Every rule in `evaluator/criteria.py` is tagged **CONFIRMED**
(stated by him), **HISTORICAL** (seen in past models) or **HYPOTHESIS** (pending his confirmation).

## How it decides
```
0  THESIS       the developer's line (vocation, markets, land size, max ticket); no fit -> discarded, no math
1  GATES        title / power to transfer / community opposition -> NO-GO (land)
                current zoning, protected area, non-remediable physics, critical feasibility,
                stalled product nearby (= no market) -> NO-GO (this vocation)
2  PRODUCT      current zoning first; the market validates price and pace (slow lowers the price, stalled kills it)
3  VALUE A      land price SOLVED so the project meets the developer's hurdles
                  for sale:  20% equity IRR AND 2.0x equity multiple, financing on
                  for rent:  12% yield on total cost as the target, exit at the signed buyer's cap
                             (forward sale) or a speculative 10%, horizon = lease-up absorption,
                             20% IRR approves
4  VALUE B      closed land comparables only (asking prices ignored)
5  MAX BID      the LOWER of A and B
6  STRUCTURE    deferral and payment in kind raise what you can pay (units priced net of the saved commission)
7  SCENARIOS    market-evidence scenarios -> negotiation space (no arbitrary fixed stress)
8  VERDICT      GO / BORDERLINE / NO-GO / NO FIT
```
Cost comes from the specification (structure + finishes + amenities), not from the segment.
Contingency is 5% per cost block. Decisions are pre-tax. Financing is a switch; the bridge loan funds the construction
budget (hard costs), capped at 65% of the sales value (public bank terms). Quick tests: hard costs ~40% of sales value, land ~20% (never hurdles: the IRR approves).

Commercial & services follows its own route: demand of the area -> user -> format -> norm -> market -> value.
A user counts as identified only with a binding letter of intent; the investor sets the target IRR; risk factors
(tenant credit, lease term, pre-let, location, vacancy) are shown with their evidence, never as automatic adjustments;
three exits (stabilized sale, sale of rental units to small investors, hold). Format kills (access, frontage,
parking, use restrictions, oversupply, demand that cannot pay) kill the product, not necessarily the land.

## The AI part (Nebius Token Factory + NVIDIA Nemotron)
| Step | Model | Role |
|---|---|---|
| Intake | Nemotron Super (`nvidia/nemotron-3-super-120b-a12b`) | Reads a broker email into an offer file; flags missing data, never invents it |
| Red team | Nemotron Ultra (`nvidia/Nemotron-3-Ultra-550b-a55b`) | Gets the buyer's rules and the deterministic result; returns the most fragile input, seller questions, DD checks, a payment structure that keeps capital unexposed while risks are open, and a negotiation line |
| Market context | Tavily search | Listings shown as context only; they never enter value B |

**Where Token Factory accelerated the work.** One OpenAI-compatible endpoint gave us two Nemotron sizes with the
same small stdlib client (`evaluator/llm.py`, no SDK): a fast model for intake and the 550B Ultra for the red team, swapped by changing a
model id. `/v1/models` lets the app discover served ids at runtime, so no SDK, GPU or model hosting was needed and
the whole AI layer runs inside a free Vercel function.

**The model never does the math and never sets the verdict.** If an AI step fails, the deterministic
verdict stands. If a model id is not served, the app asks Token Factory's `/models` endpoint for the
closest Nemotron and retries.

## Demo
| Developer | Case | Verdict | What it shows |
|---|---|---|---|
| DEV-1 residential | A | GO | Asking 46 M under a 56.3 M max bid (closed comparables bind); deferral + in-kind units add 8.6 M vs. paying cash (48.6 M). Pro forma at max bid ≈ land 22 / hard 40 / soft+sales 10 / finance 4 / margin 21 |
| DEV-1 | B | NO-GO | Hard costs at 64% of sales (standard ~40%): supports only 10.7 M against 25 M asked; no scenario rescues it |
| DEV-1 | C | BORDERLINE | 54 M asked fits under 55.0 M, but a critical feasibility is open: payments tied to its accreditation |
| DEV-1 | G | NO-GO (land) | Uncertain title kills the land before any math |
| DEV-1 | H | NO FIT | Wrong market and size for this developer: discarded in one step |
| DEV-3 build-to-rent | D | GO | Forward sale at an 8.5% cap supports 63.4 M; without a signed buyer (speculative 10%) only 31.6 M |
| DEV-4 commercial | I | BORDERLINE | Proximity centre with an AAA anchor in talks: speculative (12% standard exit cap) supports 20.8 M against 30 M asked; only a **binding** LOI (9.5% cap) supports it (35.8 M), so the land is not paid before it is signed. Risk factors are listed as evidence, never as automatic % |
| DEV-2 industrial | E | GO | Net area after easements, lot types with different absorption, open infrastructure |
| — | F | No automatic verdict | Land banking: partial protocol, checklist, no invented price |

## Run
```bash
python3 -m unittest discover -s tests                     # 20 tests
python3 -m evaluator.cli cases/case_c_residential_borderline.json --thesis developers/dev1_residential.json --lang es
export NEBIUS_API_KEY=...  TAVILY_API_KEY=...             # optional AI steps
python3 server.py                                          # http://localhost:7860
```
Stdlib only, no dependencies. `DEMO_MOCK=1` shows the UI with labelled mock AI output.
Spend guards: `MAX_LLM_CALLS_PER_RUN`, `DAILY_AI_CAP`.

Deploy: `vercel.json` + `api/*.py` run the same API as Vercel Python functions; set `NEBIUS_API_KEY`
and `TAVILY_API_KEY` as environment variables. A `Dockerfile` is included for container hosts.

## Repository map
`evaluator/` engine (criteria, gates, thesis, protocols, debt, memo, LLM and agent layers) ·
`cases/` fictitious offers · `developers/` fictitious developer theses · `api/` serverless functions ·
`index.html` UI (English / Spanish) · `docs/` PRD, spec, video script.

## License
MIT
