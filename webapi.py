"""Shared JSON API (local server and Vercel functions). Stdlib only.
Spend guard: a cap on AI-assisted evaluations per instance per day, so a public demo cannot drain free credits."""
from __future__ import annotations
import glob, json, os, time
from evaluator import agent

ROOT = os.path.dirname(os.path.abspath(__file__))
DAILY_AI_CAP = int(os.environ.get("DAILY_AI_CAP", "150"))
_state = {"day": time.strftime("%Y-%m-%d"), "ai_used": 0}


def _load(pattern):
    return [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(ROOT, pattern)))]


CASES = _load("cases/*.json")
DEVELOPERS = {d["developer_id"]: d for d in _load("developers/*.json")}


def ai_allowed() -> bool:
    today = time.strftime("%Y-%m-%d")
    if _state["day"] != today:
        _state.update(day=today, ai_used=0)
    return _state["ai_used"] < DAILY_AI_CAP


def thesis_for(offer: dict, dev_id):
    if dev_id == "none":
        return None
    if dev_id in DEVELOPERS:
        return DEVELOPERS[dev_id]
    return next((d for d in DEVELOPERS.values() if d["vocation"] == offer.get("vocation")), None)


def get(path: str):
    if path.startswith("/api/cases"):
        return 200, CASES
    if path.startswith("/api/developers"):
        return 200, list(DEVELOPERS.values())
    if path.startswith("/api/evaluate"):  # diagnostics: which Nemotron ids Token Factory serves (no secrets)
        from evaluator import llm
        if not llm.available():
            return 200, {"ai": False}
        try:
            return 200, {"ai": True, "nemotron_models": [m for m in llm.list_models() if "nemotron" in m.lower()]}
        except Exception as e:
            return 200, {"ai": True, "error": f"{type(e).__name__}: {e}"}
    return 404, {"error": "not found"}


def post(path: str, req: dict):
    try:
        lang = req.get("lang", "en")
        if path.startswith("/api/intake"):
            if not ai_allowed():
                return 429, {"error": "daily AI cap reached; fill the offer file manually"}
            _state["ai_used"] += 1
            return 200, agent.intake(str(req.get("text", ""))[:6000])
        if path.startswith("/api/evaluate"):
            use_ai = bool(req.get("use_ai")) and ai_allowed()
            if use_ai:
                _state["ai_used"] += 1
            out = agent.run(req["offer"], lang=lang, use_ai=use_ai, market=str(req.get("market", ""))[:120],
                            thesis=thesis_for(req["offer"], req.get("developer_id")))
            out = json.loads(json.dumps(out, default=str))
            out["ai"]["cap_left"] = max(0, DAILY_AI_CAP - _state["ai_used"])
            return 200, out
        return 404, {"error": "not found"}
    except (KeyError, ValueError, TypeError) as e:
        return 400, {"error": str(e)}
