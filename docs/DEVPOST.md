# Devpost submission text (Nebius x NVIDIA Global AI Hackathon)

**Project name:** Land Negotiator
**Tagline:** How much to pay for land, and how to pay it: a developer's 20-year criterion, made executable with NVIDIA Nemotron on Nebius.
**Track:** Best Apps and Agents

## Inspiration
In Mexico and Latin America, land offers arrive as WhatsApp messages and broker emails, and are answered by intuition or by spreadsheets with hidden assumptions. The land price agreed on day one decides the margin of a three-year project. Experienced developers carry a precise criterion in their heads; junior teams and investors do not have it.

## What it does
Land Negotiator takes a land offer and returns a committee-ready answer:
- **Thesis fit**: is this offer even in the developer's line (vocation, market, land size, ticket)? If not, it is discarded before any math.
- **Kill gates**: uncertain title or material community opposition kills the land; current zoning, physical limits, critical utilities or a stalled local market kill that product.
- **Maximum bid**: the land price is solved so the project still meets the developer's hurdles (for sale: 20% equity IRR and 2.0x equity multiple with financing; for rent: a 12% yield-on-cost target, exit at the signed buyer's cap or a speculative 10%, horizon set by lease-up absorption, 20% IRR approves). The bid is the lower of that and closed land comparables.
- **Payment structure**: shows how deferral and payment in kind raise what the buyer can pay.
- **Negotiation space**: market-evidence scenarios instead of an arbitrary stress test.
- **AI red team**: NVIDIA Nemotron attacks the inputs, writes the questions for the seller and the due-diligence checks, proposes a structure that keeps capital unexposed, and drafts a negotiation line.

## How we built it
- Deterministic engine in pure Python (no dependencies): monthly cash flows, IRR, a hurdle solver with a construction-loan switch, and one protocol per land vocation (residential for sale, build-to-rent, industrial lots; partial checklists where the criterion is not yet complete, so no price is invented).
- **Nebius Token Factory** (OpenAI-compatible API) with **NVIDIA Nemotron**: Nemotron Super for intake (email to structured offer), Nemotron Ultra as the red team. The models receive the rules and the computed result; they never compute numbers or set the verdict.
- **Tavily** search for market context, shown as context only and never used as a comparable.
- The criterion itself came from structured interviews with a developer, contrasted with his historical models and public references; every rule carries its provenance (confirmed, historical, hypothesis).
- Stdlib web server locally; Vercel Python functions for the public demo.

## Challenges
Turning tacit judgement into rules without inventing any: when the developer had not stated a rule, the tool says so instead of guessing. Keeping the LLM out of the math while still making it useful. Reconciling simple rules (20% IRR, 2.0x, 12% yield) inside one solver with financing.

## Accomplishments
Eight end-to-end demo cases across three developer theses, 14 automated tests, every number reproducible, bilingual interface (English / Spanish), and an AI layer that improves the negotiation without touching the verdict.

## What we learned
In land, the payment structure is as important as the price, and a signed buyer's cap can double what the land is worth. The most valuable AI output was not a number: it was the right question to ask the seller.

## What's next
Protocols for commercial, mixed-use, tourism, agricultural and conservation land; comparable homologation across similar zones; a seller-side view to compare competing offers.

## Built with
Python, NVIDIA Nemotron, Nebius Token Factory, Tavily, Vercel, HTML/JS.

## Links
- Demo: (Vercel URL)
- Repository: (GitHub URL)
- Video: (YouTube URL)
