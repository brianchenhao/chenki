const steps = [
  {
    n: "1",
    title: "Install the client",
    body: "pip install chenki. One runtime dep (httpx). No vendor SDK lock-in.",
  },
  {
    n: "2",
    title: "Point at any OpenAI-compatible endpoint",
    body: "ChenkiClient() defaults to the free chenki-llm Hugging Face Space. Or pass your own endpoint — Ollama, vLLM, llama.cpp, LM Studio, OpenAI itself.",
  },
  {
    n: "3",
    title: "Use the restaurant helpers",
    body: "ask_about_menu, classify_dish, parse_order_text — return typed dataclasses, prompt-injection-safe by default.",
  },
]

const DIAGRAM = `┌─────────────────────────┐
│   Adopter's Python App  │
│   ─ ChenkiClient        │
│   ─ ask_about_menu      │
│   ─ classify_dish       │
└────────────┬────────────┘
             │ HTTPS  /v1/chat/completions
             ▼
┌─────────────────────────────────┐
│  chenki-llm (HF Space)          │
│  ─ Qwen 2.5 1.5B Q4_K_M         │
│  ─ llama.cpp:server             │
│  ─ OpenAI-compatible API        │
└─────────────────────────────────┘`

export default function HowItWorks() {
  return (
    <section className="bg-white py-20">
      <div className="mx-auto max-w-5xl px-6">
        <h2 className="text-3xl md:text-4xl font-semibold text-gray-900 text-center">
          How it works
        </h2>

        <div className="mt-12 grid md:grid-cols-3 gap-6">
          {steps.map((s) => (
            <div
              key={s.n}
              className="rounded-xl border border-gray-200 p-6 hover:border-chenki-300 hover:shadow-sm transition"
            >
              <div className="w-9 h-9 rounded-full bg-chenki-100 text-chenki-700 font-semibold flex items-center justify-center">
                {s.n}
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900">
                {s.title}
              </h3>
              <p className="mt-2 text-gray-600 text-sm leading-relaxed">
                {s.body}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-14">
          <h3 className="text-lg font-semibold text-gray-900 text-center">
            Architecture
          </h3>
          <pre className="mt-4 mx-auto max-w-2xl bg-gray-50 border border-gray-200 rounded-lg p-6 font-mono text-xs md:text-sm text-gray-700 overflow-x-auto whitespace-pre">
{DIAGRAM}
          </pre>
          <p className="mt-4 text-sm text-gray-500 text-center max-w-2xl mx-auto">
            Self-hosters can deploy their own Space with the included{" "}
            <code className="font-mono">server/Dockerfile</code> — same image, same API, zero third-party egress.
          </p>
        </div>
      </div>
    </section>
  )
}
