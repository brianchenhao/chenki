export default function Hero() {
  return (
    <header className="relative overflow-hidden bg-gradient-to-br from-chenki-700 via-chenki-600 to-chenki-pink text-white">
      <div className="mx-auto max-w-4xl px-6 py-24 md:py-32 text-center">
        <p className="inline-block rounded-full bg-white/10 px-3 py-1 text-xs font-medium tracking-wide uppercase backdrop-blur-sm">
          v0.1.0 · self-hostable · MIT
        </p>
        <h1 className="mt-6 text-4xl md:text-6xl font-bold tracking-tight leading-tight">
          Self-hostable LLM client<br />for restaurant tech.
        </h1>
        <p className="mt-6 text-lg md:text-xl text-white/85 max-w-2xl mx-auto leading-relaxed">
          A thin Python library that talks to any OpenAI-compatible{" "}
          <code className="px-1.5 py-0.5 rounded bg-white/15 text-white font-mono text-sm">
            /v1/chat/completions
          </code>
          {" "}endpoint, with restaurant-domain helpers built on top.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <a
            href="#install"
            className="rounded-md bg-white text-chenki-700 hover:bg-chenki-50 font-medium px-6 py-3 transition"
          >
            Install
          </a>
          <a
            href="https://github.com/brianchenhao/chenki"
            target="_blank"
            rel="noopener"
            className="rounded-md border border-white/30 hover:bg-white/10 font-medium px-6 py-3 transition"
          >
            GitHub
          </a>
        </div>
      </div>
    </header>
  )
}
