export default function Footer() {
  return (
    <footer className="mt-auto bg-gray-900 text-gray-300 py-10">
      <div className="mx-auto max-w-5xl px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
        <p className="font-mono">chenki · MIT licensed</p>
        <nav className="flex items-center gap-6">
          <a
            href="https://github.com/brianchenhao/chenki"
            target="_blank"
            rel="noopener"
            className="hover:text-white transition"
          >
            GitHub
          </a>
          <a
            href="https://docs.chenki.com"
            className="hover:text-white transition"
          >
            Docs
          </a>
          <a
            href="https://pypi.org/project/chenki"
            target="_blank"
            rel="noopener"
            className="hover:text-white transition"
          >
            PyPI
          </a>
          <a
            href="https://huggingface.co/spaces/brianchenhao/chenki-llm"
            target="_blank"
            rel="noopener"
            className="hover:text-white transition"
          >
            HF Space
          </a>
        </nav>
      </div>
    </footer>
  )
}
