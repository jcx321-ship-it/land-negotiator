# Devpost submission text (Nebius x NVIDIA Global AI Hackathon)

**Project name:** Land Negotiator
**Tagline:** How much to pay for land, and how to pay it: a developer's 20-year criterion, made executable with NVIDIA Nemotron on Nebius Token Factory.
**Track:** Best Apps and Agents

## Inspiration
In Mexico and Latin America, land offers arrive as WhatsApp messages and broker emails and are answered by intuition or by spreadsheets with hidden assumptions. The land price agreed on day one decides the margin of a three-year project. Experienced developers carry a precise criterion in their heads; junior teams and investors do not.

## What it does
Land Negotiator takes a land offer and returns a committee-ready answer:
- **Thesis fit**: is the offer in the developer's line (vocation, market, land size, ticket, format requirements)? If not, it is discarded before any math.
- **Kill gates**: uncertain title kills the land; current zoning, physical limits, utilities, a stalled market or (for retail) access, visibility, frontage and parking kill only that product.
- **Maximum bid**: the land price is solved so the project still meets the investor's hurdles, with a bridge loan on hard construction costs:
  - *For sale*: 20% equity IRR and 2.0x equity multiple, plus quick sanity tests (hard costs about 40% of sales; a 20/40/10/5/5/20 pro forma).
  - *Build-to-rent*: 12% yield-on-cost target, exit at the signed buyer's cap or a speculative cap.
  - *Commercial & services*: demand first; a user only counts as identified with a binding letter of intent; three exit routes (stabilized sale, sale of rental units to small investors, hold); risk factors shown as evidence, never as automatic percentages; the investor sets the target IRR.
  - *Industrial lots*; partial checklists where the criterion is not complete, so no price is invented.
  The bid is the lower of the project value and closed land comparables (asking prices are ignored).
- **Payment structure**: shows how deferral and payment in kind raise what the buyer can pay.
- **Negotiation space**: market-evidence scenarios; a borderline verdict says exactly which scenario must be secured before paying the asking price.
- **AI red team**: NVIDIA Nemotron attacks the inputs, writes the questions for the seller and the due-diligence checks, proposes a structure that keeps capital unexposed and drafts a negotiation line.

## How we built it
- Deterministic engine in pure Python (no dependencies): monthly cash flows, IRR, a hurdle solver with a capped bridge loan, and one protocol per land vocation.
- **Nebius Token Factory** (OpenAI-compatible API) with **NVIDIA Nemotron**: a Nemotron model for intake (broker email to structured offer, with a guard that drops invented numbers) and Nemotron Ultra as the red team. Models receive the rules and the computed result; they never compute numbers or set the verdict.
- Optional Tavily search for market context, shown as context only, never as a comparable.
- The criterion came from structured interviews with a developer, contrasted with public references; every rule carries its provenance (confirmed, historical, hypothesis).
- Vercel Python functions for the public demo; 19 automated tests.

## Challenges
Turning tacit judgement into rules without inventing any: when the developer had not stated a rule, the tool says so instead of guessing. Keeping the LLM out of the math while making it useful. Reasoning models returning thoughts instead of JSON: solved with a robust parser and a per-request call guard. Reconciling simple rules (20% IRR, 2.0x, 12% yield, a bridge loan on hard costs) inside one solver.

## Accomplishments
Nine end-to-end demo cases across four developer theses, 19 tests, every number reproducible, an English/Spanish interface, and an AI layer that improves the negotiation without touching the verdict. In the commercial demo, Nemotron Ultra singled out the anchor tenant's letter of intent as the most fragile input; the engine shows the same land is worth 20.8 M speculative and 35.8 M with a binding LOI.

## What we learned
In land, the payment structure matters as much as the price, and a signed user or buyer can change what the land is worth by more than half. The most valuable AI output was not a number: it was the right question to ask the seller.

## What's next
Protocols for mixed-use, tourism, agricultural and conservation land; comparable homologation across zones; a seller-side view to compare competing offers.

## Built with
Python, NVIDIA Nemotron, Nebius Token Factory, Vercel, HTML/JS, Tavily (optional).

## Links
- Demo: https://land-negotiator.vercel.app
- Repository: https://github.com/jcx321-ship-it/land-negotiator
- Video: (YouTube URL)

All demo data is fictitious.
