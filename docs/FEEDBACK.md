# Feedback on Nebius Token Factory and NVIDIA Nemotron (from building Land Negotiator)

**Context.** A solo, non-developer founder built a land-deal negotiation agent in four weeks: Nemotron reads broker
emails and red-teams the deal; deterministic Python computes the maximum bid. Everything runs on a free Vercel
function calling Token Factory. These notes come from that build.

## 1. What we were trying to do
Use one hosted endpoint for two very different jobs: fast, strict extraction (email → JSON offer, no invented
numbers) and slow, adversarial reasoning (attack the deal, write seller questions), without hosting models or
installing an SDK.

## 2. What worked
- **OpenAI-compatible API**: a small standard-library client (`evaluator/llm.py`) was enough; no SDK, which kept the
  serverless function small and cold starts fast.
- **`GET /v1/models`**: the app resolves served Nemotron ids at runtime, so catalog renames did not break the demo.
- **Model range on one key**: switching between a fast Nemotron for intake and Nemotron 3 Ultra (550B) for the red
  team is a one-line change. Ultra followed a strict instruction ("attack the inputs, never change the verdict")
  reliably, and its seller questions were the most valuable AI output in the product.

## 3. What slowed us down (with the fix we had to build)
| Friction | Impact | Our workaround | Suggested fix |
|---|---|---|---|
| Reasoning models put the answer in `reasoning_content`, leave `content` empty or cut it at `finish_reason=length` | Intake and red team failed with JSON errors on the live demo | Raw-decode JSON parser, split on `</think>`, larger `max_tokens` (2,500 / 4,000) | A documented per-call switch for "final answer only", and a clear note per model on where the answer is returned |
| No structured-output / JSON mode flag visible per model in the catalog | Trial and error to know which models honour `response_format` | Prompt-only JSON plus a tolerant parser | A "supports JSON mode / tool calls" column in the model catalog |
| Model ids differ in casing and separators (`Nemotron-3_5-Lightning` vs `nemotron-3-super-120b-a12b`) | Hard-coded ids broke when we changed models | Fuzzy resolution against `/v1/models` | Stable lowercase aliases (e.g. `nemotron-ultra-latest`) |
| No per-key spend cap in the console | A public demo could drain credits | App-side daily cap (`DAILY_AI_CAP`) and per-request call guard | Per-key monthly and daily spend limits, and read-only "demo keys" |

## 4. What we would like next
- Latency and throughput hints per model in the catalog, to pick intake vs. red-team models without benchmarking.
- A small "deploy to Vercel / serverless" quick-start in the Token Factory docs: it is the fastest path for app
  builders and needs only the env var and the base URL.
- Examples of Nemotron used as a critic or red team (not only as a chatbot): it is a strong pattern for
  decision tools where the numbers must stay deterministic.
