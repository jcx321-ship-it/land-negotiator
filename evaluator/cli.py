"""Usage: python -m evaluator.cli cases/case_a_residential_go.json [--lang es] [--out memo.md]"""
from __future__ import annotations
import argparse, json
from .engine import evaluate_offer
from .memo import render


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Land offer evaluator (Founder criterion).")
    ap.add_argument("case"); ap.add_argument("--lang", choices=["en", "es"], default="en"); ap.add_argument("--out"); ap.add_argument("--thesis", help="developer thesis JSON")
    a = ap.parse_args(argv)
    th = json.load(open(a.thesis, encoding="utf-8")) if a.thesis else None
    r = evaluate_offer(json.load(open(a.case, encoding="utf-8")), th)
    text = render(r, a.lang)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
