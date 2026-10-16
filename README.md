# Land Negotiator

**How much to pay for land, and how to pay it.** A senior Mexican developer's 20-year land-buying criterion,
made executable. Paste an offer; get the thesis fit, the kill gates, the maximum bid, how the payment
structure changes it, market scenarios for the negotiation, and an AI red team that attacks the inputs
before you sign.

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
Contingency is 5% per cost block. Decisions are pre-tax. Financing is a switch.

## The AI part (Nebius Token Factory + NVIDIA Nemotron)
| Step | Model | Role |
|---|---|---|
| Intake | Nemotron Super (`nvidia/nemotron-3-super-120b-a12b`) | Reads a broker email into an offer file; flags missing data, never invents it |
| Red team | Nemotron Ultra (`nvidia/Nemotron-3-Ultra-550b-a55b`) | Gets the buyer's rules and the deterministic result; returns the most fragile input, seller questions, DD checks, a payment structure that keeps capital unexposed while risks are open, and a negotiation line |
| Market context | Tavily search | Listings shown as context only; they never enter value B |

**The model never does the math and never sets the verdict.** If an AI step fails, the deterministic
verdict stands. If a model id is not served, the app asks Token Factory's `/models` endpoint for the
closest Nemotron and retries.

## Demo
| Developer | Case | Verdict | What it shows |
|---|---|---|---|
| DEV-1 residential | A | GO | Asking 24 M under a 27.5 M max bid; deferral + in-kind units add 6.4 M vs. cash (21.0 M) |
| DEV-1 | B | NO-GO | Supports only 5.9 M (the 2.0x multiple binds) against 25 M asked; no scenario rescues it |
| DEV-1 | C | BORDERLINE | 28.5 M asked vs 27.5 M; only the anchor-employer scenario (30.0 M) covers it, and a feasibility is open |
| DEV-1 | G | NO-GO (land) | Uncertain title kills the land before any math |
| DEV-1 | H | NO FIT | Wrong market and size for this developer: discarded in one step |
| DEV-3 build-to-rent | D | GO | Forward sale at an 8.5% cap supports 58.1 M; without a signed buyer (speculative 10%) only 26.4 M |
| DEV-2 industrial | E | GO | Net area after easements, lot types with different absorption, open infrastructure |
| — | F | No automatic verdict | Land banking: partial protocol, checklist, no invented price |

## Run
```bash
python3 -m unittest discover -s tests                     # 14 tests
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
