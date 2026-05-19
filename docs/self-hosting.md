# Self-hosting chenki-llm

Half the point of chenki is that you can run the inference server yourself. The public Space at `brianchenhao-chenki-llm.hf.space` is convenient for demos, but customer prompts transit through Hugging Face's infrastructure — not what you want for PDPA (Malaysia), GDPR (EU), HIPAA, or any other data-residency-sensitive deployment.

This page walks through deploying your own copy.

## Option A — Hugging Face Space (zero infra)

Fastest path. Free CPU tier is enough for 8–12 tok/s on Qwen 2.5 1.5B Q4_K_M.

### 1. Create a new Docker Space

Go to <https://huggingface.co/new-space>, set:

- **Owner:** your HF username or org
- **Space name:** `chenki-llm` (or anything you like)
- **SDK:** Docker
- **Hardware:** CPU basic (free) — or upgrade to a paid tier for faster inference
- **License:** MIT

Click Create. You'll get an empty Space.

### 2. Push the Dockerfile + README

```bash
git clone https://huggingface.co/spaces/<your-user>/<your-space>
cp /path/to/chenki/server/* <your-space>/
cd <your-space>
git add Dockerfile README.md
git commit -m "deploy chenki-llm"
git push
```

The Dockerfile (~20 lines) pulls the `llama.cpp:server` image and curls down Qwen 2.5 1.5B Instruct Q4_K_M (~1 GB) at build time. First build takes 3–5 minutes; subsequent builds use Docker's layer cache.

### 3. Wait for `Running`

Watch the build at `https://huggingface.co/spaces/<your-user>/<your-space>`. Status flips from `Building` → `Running`. The Space exposes:

- `GET  /health` → `{"status":"ok"}`
- `POST /v1/chat/completions` — OpenAI-compatible
- `GET  /v1/models`
- `GET  /props` — llama-server runtime settings

### 4. Point chenki at it

```python
from chenki import ChenkiClient, ChenkiConfig

client = ChenkiClient(
    config=ChenkiConfig(
        endpoint="https://<your-user>-<your-space>.hf.space/v1"
    )
)
```

That's it. No code in your application changes; only the endpoint URL.

## Option B — Docker on your own VPS

For deployments where even HF infrastructure is too third-party.

```bash
docker run -d --name chenki-llm \
  -p 7860:7860 \
  ghcr.io/ggml-org/llama.cpp:server \
  -m /tmp/model.gguf \
  --host 0.0.0.0 --port 7860 \
  -c 4096 -t 2
```

You'll need to download the GGUF file separately and mount it, or build a Dockerfile that bakes it in (same one chenki's `server/Dockerfile` uses).

Hardware sizing:

| Model | RAM | Throughput on 2 vCPU |
|---|---|---|
| Qwen 2.5 1.5B Q4_K_M | ~1.5 GB | 8–12 tok/s |
| Qwen 2.5 3B Q4_K_M | ~2.5 GB | 4–6 tok/s |
| Llama 3.2 3B Q4_K_M | ~2.5 GB | 4–6 tok/s |
| Phi-3.5 Mini Q4_K_M | ~3 GB | 3–5 tok/s |

For more headroom move to a GPU-backed Space or use `vllm` instead of `llama.cpp`.

## Picking a different model

Any GGUF that `llama.cpp` supports works. Change the curl URL in the Dockerfile:

```dockerfile
RUN curl -L -o model.gguf \
    https://huggingface.co/<repo>/<file>.gguf
```

Then the model name passed by chenki (`config.model`) is informational — `llama-server` doesn't validate it. If you want to swap models on the server side without touching client code, do it here.

## Data flow with a self-hosted Space

```
Adopter app  ──HTTPS──>  your chenki-llm Space  ──>  Qwen running on your tenant's CPU
                              │
                              └─ no traffic to OpenAI, Anthropic, Google, or anyone else
```

Chenki itself stores **nothing**. Even the optional local cache (off by default) is on the adopter's own disk. The only data that leaves the adopter's process is the prompt text sent over HTTPS to the configured endpoint.

For Geyam's specific deployment, this means cashier questions about the menu never traverse a third-party LLM provider — they go to a Hugging Face Space the shop owner controls.

## Hardening checklist for production

- [ ] Pin the GGUF SHA in the Dockerfile so a model upstream rename doesn't break your build.
- [ ] Use a paid HF Space tier (or your own infra) — free Spaces sleep after inactivity, adding ~30 s cold-start to the first request.
- [ ] Put a thin proxy in front (Caddy, nginx) if you want auth, rate limiting, or per-tenant quotas.
- [ ] If you care about latency floors, switch from `llama.cpp` Q4_K_M to vllm + an FP16 model on GPU.
- [ ] Monitor `total_tokens` from each response — that's your inference cost on paid hardware.
