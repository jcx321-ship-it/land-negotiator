"""Agentic layer: intake (fast Nemotron) -> deterministic engine -> market context (Tavily) -> red team
(Nemotron Ultra) -> memo. The models question inputs and draft text; they never set the verdict or the numbers."""
from __future__ import annotations
import json, os, urllib.request
from . import llm
from .engine import evaluate_offer
from .memo import render
from .criteria import RULES

ULTRA_MODEL = os.environ.get("NEMOTRON_REASONING_MODEL", "nvidia/Nemotron-3-Ultra-550b-a55b")
TAVILY_URL = "https://api.tavily.com/search"
MOCK = os.environ.get("DEMO_MOCK") == "1"

RED_TEAM_PROMPT = """You are the red team of a land acquisition committee in Mexico. The buyer's criterion:
{rules}
You receive the deterministic evaluation (do NOT recompute or change numbers or verdict) and the seller's notes.
Attack the INPUTS and the open risks. Return ONE JSON object (no prose) with keys:
 fragile_input, why (2 sentences using the given numbers), questions_for_seller (3), site_and_dd_checks (3),
 structure_proposal (how to defer or pay in kind so capital is not exposed while risks are open),
 negotiation_line (anchored on max_bid and the scenario range). Language: {lang}."""


def intake(text: str) -> dict:
    llm._calls = 0  # the spend guard counts calls per request, not per warm serverless instance
    if MOCK:
        return {"_mock": True, "vocation": "residential_sale", "notes": "MOCK: values not read from text"}
    return llm.extract_offer(text)


def research(market: str, lang: str = "en") -> dict | None:
    key = os.environ.get("TAVILY_API_KEY")
    if not market or not (key or MOCK):
        return None
    if MOCK:
        return {"_mock": True, "query": market, "results": [{"title": "MOCK source", "url": "https://example.com", "content": "MOCK"}]}
    q = (f"precio de venta de terrenos {market} 2026" if lang == "es" else f"land sale prices {market} 2026")
    body = json.dumps({"query": q, "max_results": 5, "search_depth": "basic"}).encode()
    req = urllib.request.Request(TAVILY_URL, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return {"query": q, "results": [{"title": r.get("title"), "url": r.get("url"), "content": (r.get("content") or "")[:400]}
                                    for r in data.get("results", [])],
            "note": "Context only: listings are asking prices and never enter value B (closed transactions only)."}


def red_team(result: dict, notes: str, ctx: dict | None, lang: str = "en") -> dict | None:
    if MOCK:
        return {"_mock": True, "fragile_input": "absorption", "why": "MOCK", "questions_for_seller": ["MOCK"] * 3,
                "site_and_dd_checks": ["MOCK"] * 3, "structure_proposal": "MOCK", "negotiation_line": "MOCK"}
    if not llm.available():
        return None
    keep = ("vocation", "thesis_fit", "verdict", "reasons", "asking_price", "value_A_project", "value_B_comparables", "max_bid",
            "scenarios", "open_risks", "pending_dd", "quick_tests")
    payload = {k: result.get(k) for k in keep}
    payload["seller_notes"] = notes
    if ctx:
        payload["market_context_snippets"] = [r["content"] for r in ctx["results"]][:5]
    rules = "\n".join(f"- {t}" for _, t in RULES)
    out = llm._chat([{"role": "system", "content": RED_TEAM_PROMPT.format(rules=rules, lang="Spanish" if lang == "es" else "English")},
                     {"role": "user", "content": json.dumps(payload, default=str)}], ULTRA_MODEL, max_tokens=int(os.environ.get("RED_TEAM_MAX_TOKENS", "4000")), json_mode=True)
    return llm.parse_json(out)


def run(offer: dict, lang: str = "en", use_ai: bool = True, market: str = "", thesis: dict | None = None) -> dict:
    llm._calls = 0
    result = evaluate_offer(offer, thesis)
    out = {"result": result, "ai": {"enabled": use_ai and (llm.available() or MOCK)}}
    if use_ai and result.get("verdict") != "NO FIT":
        try:
            ctx = research(market, lang)
            out["research"] = ctx
            out["red_team"] = red_team(result, offer.get("notes", ""), ctx, lang)
        except Exception as e:
            out["ai"]["error"] = f"{type(e).__name__}: {e}"
        out["ai"]["model"] = llm.LAST.get("model")
    out["memo_md"] = render(result, lang)
    return out
