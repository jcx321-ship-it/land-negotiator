"""Optional Nemotron layer on Nebius Token Factory (OpenAI-compatible API).

Two jobs only:
  1. extract_offer(): turn a free-text offer (broker email, listing) into the structured sheet.
  2. narrative(): write a short analyst note from numbers the model already computed.
The model never produces the numbers in the verdict. Without NEBIUS_API_KEY the app runs fully
deterministic and says so.
"""
from __future__ import annotations
import json, os, urllib.request, urllib.error

BASE_URL = os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
# Model ids as listed in the public Token Factory catalog (checked 2026-10-01). If an id is not served,
# resolve_model() asks the /models endpoint for the closest NVIDIA Nemotron and retries once.
FAST_MODEL = os.environ.get("NEMOTRON_FAST_MODEL", "nvidia/nemotron-3-super-120b-a12b")
_resolved: dict[str, str] = {}


def list_models() -> list[str]:
    req = urllib.request.Request(BASE_URL.rstrip("/") + "/models",
                                 headers={"Authorization": f"Bearer {os.environ['NEBIUS_API_KEY']}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return [m["id"] for m in json.load(resp).get("data", [])]


def resolve_model(wanted: str) -> str:
    """Pick the served model closest to `wanted` (same family word: ultra / super / nano), NVIDIA Nemotron only."""
    if wanted in _resolved:
        return _resolved[wanted]
    ids = [i for i in list_models() if "nemotron" in i.lower()]
    if wanted in ids or not ids:
        _resolved[wanted] = wanted
        return wanted
    w = wanted.lower()
    for fam in ("ultra", "super", "nano", "lightning"):
        if fam in w:
            hit = [i for i in ids if fam in i.lower()]
            if hit:
                _resolved[wanted] = sorted(hit, key=len)[0]
                return _resolved[wanted]
    _resolved[wanted] = ids[0]
    return ids[0]
# JSON mode is not tagged on Nemotron models in the catalog: ask for JSON in the prompt and validate it.
USE_RESPONSE_FORMAT = os.environ.get("USE_RESPONSE_FORMAT") == "1"
MAX_CALLS = int(os.environ.get("MAX_LLM_CALLS_PER_RUN", "4"))  # spend guard
_calls = 0


def available() -> bool:
    return bool(os.environ.get("NEBIUS_API_KEY"))


def _chat(messages: list[dict], model: str, max_tokens: int = 600, json_mode: bool = False) -> str:
    global _calls
    if _calls >= MAX_CALLS:
        raise RuntimeError("LLM call budget for this run exhausted (spend guard).")
    _calls += 1
    model = _resolved.get(model, model)
    for attempt in (0, 1):
        body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2}
        if json_mode and USE_RESPONSE_FORMAT:
            body["response_format"] = {"type": "json_object"}
        req = urllib.request.Request(BASE_URL.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {os.environ['NEBIUS_API_KEY']}",
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=150) as resp:
                msg = json.load(resp)["choices"][0]["message"]
                LAST["model"] = model
                return msg.get("content") or msg.get("reasoning_content") or ""
        except urllib.error.HTTPError as e:
            if attempt == 0 and e.code in (400, 404):
                model = resolve_model(model)
                continue
            raise
    raise RuntimeError("unreachable")


LAST: dict = {}


EXTRACT_PROMPT = """You extract a land purchase offer into ONE JSON object (no prose, no code fences) with keys:
vocation (residential_sale | rental | industrial_lots | land_banking | carbon | agricultural | unknown),
asking_price, land_area_m2, far (current zoning only), sale_price_m2, rent_m2_month, hard_cost_m2,
payment_terms (text), title_status (text), zoning_status (text), feasibilities (text), notes.
Numbers in MXN and m2. If a value is missing, use null and list it in notes. Never invent values."""


def extract_offer(text: str) -> dict:
    out = _chat([{"role": "system", "content": EXTRACT_PROMPT}, {"role": "user", "content": text}],
                FAST_MODEL, json_mode=True)
    return parse_json(out)


def parse_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("{"):]
    i, j = t.find("{"), t.rfind("}")
    return json.loads(t[i:j + 1])


NARRATIVE_PROMPT = """You are a senior real estate development analyst. Write 4-6 sentences for an investment
committee. Use ONLY the numbers given. Say what drives the verdict, what would have to be true for the
deal to work, and what to verify on site. Do not change the verdict. Language: {lang}."""


def narrative(result: dict, lang: str = "en") -> str:
    keep = ("vocation", "verdict", "reasons", "asking_price", "value_A_project", "value_B_comparables", "max_bid", "scenarios")
    slim = {k: result.get(k) for k in keep}
    return _chat([{"role": "system", "content": NARRATIVE_PROMPT.format(lang="Spanish" if lang == "es" else "English")},
                  {"role": "user", "content": json.dumps(slim, default=str)}], FAST_MODEL)
