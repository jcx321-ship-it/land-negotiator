# Feedback on Nebius Token Factory and NVIDIA models (draft, to adjust after real use)

- OpenAI-compatible API made the integration a few lines of stdlib code; no SDK needed.
- The `/models` endpoint let the app resolve the served Nemotron id at runtime instead of hard-coding it.
- Nemotron Ultra followed a strict "do not change the verdict, attack the inputs" instruction well; Super was fast enough for intake.
- Wish list: JSON mode clearly flagged per model in the catalog; per-key spend caps in the console for public demos.
