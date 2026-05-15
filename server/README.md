---
title: Chenki LLM
emoji: 🍜
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# chenki-llm

OpenAI-compatible inference server running **Qwen 2.5 1.5B Instruct (Q4_K_M)** behind [`llama.cpp`](https://github.com/ggml-org/llama.cpp). Default backend for the [`chenki`](https://github.com/brianchenhao/chenki) Python client.

## Endpoint

```
POST https://brianchenhao-chenki-llm.hf.space/v1/chat/completions
```

Standard OpenAI chat-completions request/response shape. Also exposes `/health` and `/v1/models`.

## Specs

- 2 vCPU, 16 GB RAM (Hugging Face free tier)
- 4096-token context window
- ~8–12 tokens/sec on Qwen 2.5 1.5B Q4_K_M

## Self-host

Clone the [chenki repo's `server/`](https://github.com/brianchenhao/chenki/tree/main/server) and push the same `Dockerfile` + this `README.md` into your own Hugging Face Space for data-residency-sensitive deployments (PDPA, GDPR). Same image, same API.

```bash
git clone https://huggingface.co/spaces/<your-user>/<your-space>
cp /path/to/chenki/server/* .
git add . && git commit -m "deploy chenki-llm" && git push
```
