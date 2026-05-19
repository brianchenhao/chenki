import { useState } from "react"

const INSTALL_CMD = "pip install chenki"

const QUICKSTART = `from chenki import ChenkiClient, Message

client = ChenkiClient()
reply = client.chat([Message(role="user", content="Hello!")])
print(reply.text)`

export default function Install() {
  const [copied, setCopied] = useState(false)

  async function copy() {
    await navigator.clipboard.writeText(INSTALL_CMD)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <section id="install" className="bg-white py-20">
      <div className="mx-auto max-w-3xl px-6">
        <h2 className="text-3xl md:text-4xl font-semibold text-gray-900 text-center">
          Install
        </h2>
        <p className="mt-3 text-gray-600 text-center">
          One runtime dependency (<code className="font-mono text-sm">httpx</code>). Python 3.10+.
        </p>

        <div className="mt-8 relative">
          <pre className="bg-gray-900 text-gray-100 rounded-lg p-5 pr-20 font-mono text-sm md:text-base overflow-x-auto">
            <span className="text-chenki-pink select-none">$ </span>{INSTALL_CMD}
          </pre>
          <button
            type="button"
            onClick={copy}
            className="absolute top-3 right-3 rounded-md bg-gray-700 hover:bg-gray-600 text-gray-100 text-xs px-3 py-1.5 font-medium transition"
            aria-label="Copy install command"
          >
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>

        <h3 className="mt-12 text-xl font-semibold text-gray-900">
          30-second example
        </h3>
        <pre className="mt-3 bg-gray-50 border border-gray-200 rounded-lg p-5 font-mono text-sm overflow-x-auto text-gray-800">
{QUICKSTART}
        </pre>
      </div>
    </section>
  )
}
