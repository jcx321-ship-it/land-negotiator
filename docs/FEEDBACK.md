# Feedback on Nebius Token Factory and NVIDIA Nemotron (from building Land Negotiator)

What worked
- The OpenAI-compatible endpoint made the integration about 60 lines of standard-library Python; no SDK was needed, which kept the Vercel function small.
- `GET /v1/models` let the app discover the served Nemotron ids at runtime, so model renames did not break the demo.
- Nemotron 3 Ultra followed a strict instruction ("attack the inputs, never change the verdict") well, and its questions for the seller were the most useful AI output in the product.

Friction we hit
- Reasoning models sometimes returned the answer inside `reasoning_content` with an empty or truncated `content`, or wrapped JSON in thinking text. We had to add a raw-decode JSON parser, split on `</think>`, and raise `max_tokens` (2,500 for intake, 4,000 for the red team) to stop `finish_reason=length`.
- A JSON / structured-output mode clearly flagged per model in the catalog would remove most of that code.
- Model ids differ in casing and separators across the catalog (`Nemotron-3_5-Lightning` vs `nemotron-3-super-120b-a12b`), which makes hard-coding fragile.

Wish list
- Per-key spend caps and rate limits in the console, for public demos.
- A documented way to request "content only, no reasoning" per call.
- Latency/throughput hints per model in the catalog to choose intake vs. red-team models.
