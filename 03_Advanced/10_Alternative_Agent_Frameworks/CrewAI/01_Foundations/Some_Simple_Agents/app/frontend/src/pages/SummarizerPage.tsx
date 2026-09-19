import { useState } from 'react'
import StreamOutput from '../components/StreamOutput'
import FileUpload from '../components/FileUpload'

const INPUT_CLS = 'w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500'
const LABEL_CLS = 'block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1'

export default function SummarizerPage() {
  const [file, setFile] = useState<File | null>(null)
  const [textContent, setTextContent] = useState('')
  const [stream, setStream] = useState<ReadableStream<Uint8Array> | null>(null)
  const [finalResult, setFinalResult] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file && !textContent.trim()) return
    setLoading(true)
    setFinalResult('')
    setStream(null)

    const form = new FormData()
    if (file) {
      form.append('file', file)
    } else {
      form.append('text_content', textContent)
    }

    const res = await fetch('/api/summarizer/run', {
      method: 'POST',
      body: form,
    })
    setStream(res.body)
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">Doc Summarizer</h1>
      <p className="text-gray-500 text-sm mb-6">
        Summarize a document. Upload a file or paste text directly — quality-checked by a manager agent.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div>
          <label className={LABEL_CLS}>Upload File</label>
          <FileUpload
            accept=".txt,.md,.pdf,.docx"
            file={file}
            onFile={(f) => { setFile(f); if (f) setTextContent('') }}
            label="Click or drag a text file here"
          />
        </div>

        <div className="flex items-center gap-3 text-gray-500 text-xs">
          <hr className="flex-1 border-gray-700" />
          <span>OR paste text below</span>
          <hr className="flex-1 border-gray-700" />
        </div>

        <div>
          <label className={LABEL_CLS}>Paste Text</label>
          <textarea
            value={textContent}
            onChange={(e) => { setTextContent(e.target.value); if (e.target.value) setFile(null) }}
            rows={6}
            className={INPUT_CLS}
            placeholder="Paste your document text here..."
          />
        </div>

        <button
          type="submit"
          disabled={loading || (!file && !textContent.trim())}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2 rounded text-sm font-semibold"
        >
          {loading ? 'Summarizing...' : 'Summarize'}
        </button>
      </form>

      <StreamOutput
        stream={stream}
        onFinal={(text) => { setFinalResult(text); setLoading(false) }}
        onDone={() => setLoading(false)}
      />

      {finalResult && (
        <div className="mt-4 p-4 bg-gray-900 border border-gray-700 rounded-lg text-sm whitespace-pre-wrap text-gray-200">
          {finalResult}
        </div>
      )}
    </div>
  )
}
