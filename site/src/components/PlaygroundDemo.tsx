export default function PlaygroundDemo() {
  return (
    <section className="bg-gradient-to-b from-white to-chenki-50 py-20">
      <div className="mx-auto max-w-5xl px-6">
        <h2 className="text-3xl md:text-4xl font-semibold text-gray-900 text-center">
          Try it live
        </h2>
        <p className="mt-3 text-gray-600 text-center max-w-2xl mx-auto">
          The default backend is a free Hugging Face Space running Qwen 2.5 1.5B Instruct (Q4_K_M) behind <code className="font-mono text-sm">llama.cpp</code>. Cold start ~30 s; ~20 tok/s after.
        </p>

        <div className="mt-10 rounded-xl overflow-hidden border border-chenki-200 shadow-lg bg-white">
          <iframe
            src="https://brianchenhao-chenki-llm.hf.space"
            title="chenki-llm playground"
            className="w-full h-[640px] border-0"
            loading="lazy"
          />
        </div>

        <p className="mt-4 text-sm text-gray-500 text-center">
          Embedded from{" "}
          <a
            href="https://huggingface.co/spaces/brianchenhao/chenki-llm"
            className="underline hover:text-chenki-700"
            target="_blank"
            rel="noopener"
          >
            huggingface.co/spaces/brianchenhao/chenki-llm
          </a>
        </p>
      </div>
    </section>
  )
}
