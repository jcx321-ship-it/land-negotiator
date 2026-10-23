# Devpost submission text (Nebius x NVIDIA Global AI Hackathon)

**Project name:** Land Negotiator
**Tagline:** How much to pay for land, and how to pay it: a developer's 20-year criterion, made executable with NVIDIA Nemotron on Nebius Token Factory.
**Track:** Best Apps and Agents

## Inspiration
In Mexico and Latin America, land offers arrive as WhatsApp messages and broker emails and are answered by intuition or by spreadsheets with hidden assumptions. The land price agreed on day one decides the margin of a three-year project. Experienced developers carry a precise criterion in their heads; junior teams and investors do not.

## What it does
A broker emails a land offer. Land Negotiator turns it into a committee-ready negotiation in under a minute:
1. **Nemotron reads the email** (Nebius Token Factory) into a structured offer and flags what is missing. It never invents a number.
2. **Deterministic code decides**: thesis fit (is it in the developer's line?), kill gates (title, zoning, utilities, market), and the **maximum bid**: the land price solved so the project still meets the investor's hurdles (20% equity IRR and 2.0x for sale, 12% yield-on-cost for rent, the investor's own target for commercial), with a bridge loan on hard costs, capped by closed land comparables.
3. **Nemotron Ultra plays red team**: it attacks the most fragile assumption, writes the questions for the seller and the due-diligence checks, proposes a payment structure that keeps capital unexposed, and drafts a negotiation line. It argues; it never changes the number or the verdict.
4. The buyer sees **how payment structure changes price** (deferral and payment in kind) and **market-evidence scenarios**; a borderline verdict says exactly what must be secured before paying the asking price.

Example (fictitious): a commercial lot asked at 30 M supports 20.8 M speculative and 35.8 M only with the anchor's binding letter of intent. Nemotron Ultra singled out that letter as the weakest point and proposed paying in tranches tied to its signature.

## How it meets the judging criteria
- **Technological implementation**: two Nemotron roles on Token Factory (intake and red team) behind a stdlib client; model ids resolved at runtime; robust handling of reasoning-model output; a deterministic engine with monthly cash flows, IRR, a capped bridge-loan solver and one protocol per land vocation; 20 automated tests; spend guards for a public demo.
- **Design**: a complete flow from broker email to negotiation memo, in English and Spanish, on desktop and mobile; case I is preloaded so a judge sees the red team in one click.
- **Potential impact**: land in Mexico and Latin America is priced by intuition or hidden spreadsheets, and the price agreed on day one decides a three-year project's margin. The tool gives junior teams and investors a senior developer's criterion and the right questions before they sign.
- **Quality of the idea**: the LLM is used as an adversarial critic of a deterministic model, not as a calculator or chatbot, so numbers stay auditable and the AI adds what spreadsheets lack: doubt, questions and structure.

## How we built it
- Deterministic engine in pure Python (no dependencies): monthly cash flows, IRR, a hurdle solver with a capped bridge loan, and one protocol per land vocation.
- **Nebius Token Factory** (OpenAI-compatible API) with **NVIDIA Nemotron**: a Nemotron model for intake (broker email to structured offer, with a guard that drops invented numbers) and Nemotron Ultra as the red team. Models receive the rules and the computed result; they never compute numbers or set the verdict.
- Optional Tavily search for market context, shown as context only, never as a comparable.
- The criterion came from structured interviews with a developer, contrasted with public references; every rule carries its provenance (confirmed, historical, hypothesis).
- Vercel Python functions for the public demo; 20 automated tests.

## Challenges
Turning tacit judgement into rules without inventing any: when the developer had not stated a rule, the tool says so instead of guessing. Keeping the LLM out of the math while making it useful. Reasoning models returning thoughts instead of JSON: solved with a robust parser and a per-request call guard. Reconciling simple rules (20% IRR, 2.0x, 12% yield, a bridge loan on hard costs) inside one solver.

## Accomplishments
Nine end-to-end demo cases across four developer theses, 20 tests, every number reproducible, a full English/Spanish interface (results included), and an AI layer that improves the negotiation without touching the verdict. In the commercial demo, Nemotron Ultra singled out the anchor tenant's letter of intent as the most fragile input; the engine shows the same land is worth 20.8 M speculative and 35.8 M with a binding LOI.

## What we learned
In land, the payment structure matters as much as the price, and a signed user or buyer can change what the land is worth by more than half. The most valuable AI output was not a number: it was the right question to ask the seller.

## What's next
Protocols for mixed-use, tourism, agricultural and conservation land; comparable homologation across zones; a seller-side view to compare competing offers.

## Built during the Submission Period
The project was started from scratch on 30 September 2026, after the Submission Period opened; all code, cases and documents were created during the hackathon.

## Built with
Python, NVIDIA Nemotron, Nebius Token Factory, Vercel, HTML/JS, Tavily (optional).

## Links
- Demo: https://land-negotiator.vercel.app
- Repository: https://github.com/jcx321-ship-it/land-negotiator
- Video: (YouTube URL)

All demo data is fictitious.
