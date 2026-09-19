import { useState } from 'react'
import StreamOutput from '../components/StreamOutput'
import FileUpload from '../components/FileUpload'

const INPUT_CLS = 'w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500'
const LABEL_CLS = 'block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1'

export default function DataAnalystPage() {
  const [file, setFile] = useState<File | null>(null)
  const [instruction, setInstruction] = useState('Fix missing values and normalize numeric columns')
  const [stream, setStream] = useState<ReadableStream<Uint8Array> | null>(null)
  const [finalResult, setFinalResult] = useState('')
  const [downloadUrl, setDownloadUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    setFinalResult('')
    setDownloadUrl('')
    setStream(null)

    const form = new FormData()
    form.append('file', file)
    form.append('user_instruction', instruction)

    const res = await fetch('/api/data-analyst/run', {
      method: 'POST',
      body: form,
    })
    setStream(res.body)
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">Data Analyst</h1>
      <p className="text-gray-500 text-sm mb-6">Upload a CSV and describe your analysis task. The agent runs Python code to process it.</p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div>
          <label className={LABEL_CLS}>CSV File</label>
          <FileUpload accept=".csv" file={file} onFile={setFile} label="Click or drag a CSV file here" />
        </div>
        <div>
          <label className={LABEL_CLS}>Instruction</label>
          <textarea
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            rows={3}
            className={INPUT_CLS}
            placeholder="Describe the data transformation..."
          />
        </div>
        <button
          type="submit"
          disabled={loading || !file}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2 rounded text-sm font-semibold"
        >
          {loading ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </form>

      <StreamOutput
        stream={stream}
        onFinal={(text) => { setFinalResult(text); setLoading(false) }}
        onDownload={setDownloadUrl}
        onDone={() => setLoading(false)}
      />

      {downloadUrl && (
        <div className="mt-4 p-3 bg-gray-900 border border-indigo-700 rounded-lg flex items-center gap-3">
          <span className="text-indigo-400 text-sm">Result ready:</span>
          <a
            href={downloadUrl}
            download
            className="text-indigo-300 hover:text-indigo-100 underline text-sm font-semibold"
          >
            Download CSV
          </a>
        </div>
      )}

      {finalResult && (
        <div className="mt-4 p-4 bg-gray-900 border border-gray-700 rounded-lg text-sm whitespace-pre-wrap text-gray-200">
          {finalResult}
        </div>
      )}
    </div>
  )
}
