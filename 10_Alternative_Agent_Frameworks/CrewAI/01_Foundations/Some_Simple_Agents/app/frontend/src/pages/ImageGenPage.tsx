import { useState } from 'react'
import StreamOutput from '../components/StreamOutput'

const INPUT_CLS = 'w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500'
const LABEL_CLS = 'block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1'

export default function ImageGenPage() {
  const [prompt, setPrompt] = useState('A futuristic cityscape at sunset')
  const [stream, setStream] = useState<ReadableStream<Uint8Array> | null>(null)
  const [finalResult, setFinalResult] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setFinalResult('')
    setImageUrl('')
    setStream(null)

    const res = await fetch('/api/images/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ initial_prompt: prompt }),
    })
    setStream(res.body)
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">Image Generator</h1>
      <p className="text-gray-500 text-sm mb-6">Enhance a prompt with AI, then generate an image via DALL-E 3.</p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div>
          <label className={LABEL_CLS}>Initial Prompt</label>
          <input value={prompt} onChange={(e) => setPrompt(e.target.value)} className={INPUT_CLS} placeholder="A futuristic cityscape at sunset" />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2 rounded text-sm font-semibold"
        >
          {loading ? 'Generating...' : 'Generate Image'}
        </button>
      </form>

      <StreamOutput
        stream={stream}
        onFinal={(text) => { setFinalResult(text); setLoading(false) }}
        onImage={setImageUrl}
        onDone={() => setLoading(false)}
      />

      {imageUrl && (
        <div className="mt-4">
          <img src={imageUrl} alt="Generated" className="rounded-lg max-w-full border border-gray-700" />
          <a href={imageUrl} download className="mt-2 inline-block text-xs text-indigo-400 hover:underline">
            Download image
          </a>
        </div>
      )}

      {finalResult && !imageUrl && (
        <div className="mt-4 p-4 bg-gray-900 border border-gray-700 rounded-lg text-sm whitespace-pre-wrap text-gray-200">
          {finalResult}
        </div>
      )}
    </div>
  )
}
