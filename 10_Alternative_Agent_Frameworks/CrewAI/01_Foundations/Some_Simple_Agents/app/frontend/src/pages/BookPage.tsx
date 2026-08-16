import { useState } from 'react'
import StreamOutput from '../components/StreamOutput'

const INPUT_CLS = 'w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500'
const LABEL_CLS = 'block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1'

export default function BookPage() {
  const [userId, setUserId] = useState('user_01')
  const [preferences, setPreferences] = useState('Science fiction books with time travel themes')
  const [stream, setStream] = useState<ReadableStream<Uint8Array> | null>(null)
  const [finalResult, setFinalResult] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setFinalResult('')
    setStream(null)

    const res = await fetch('/api/books/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, user_preferences: preferences }),
    })
    setStream(res.body)
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">Book Recommender</h1>
      <p className="text-gray-500 text-sm mb-6">
        Get personalised book recommendations. Uses Mem0 memory — run twice with the same user ID to see context carry over.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div>
          <label className={LABEL_CLS}>User ID</label>
          <input value={userId} onChange={(e) => setUserId(e.target.value)} className={INPUT_CLS} placeholder="user_01" />
        </div>
        <div>
          <label className={LABEL_CLS}>Preferences</label>
          <textarea
            value={preferences}
            onChange={(e) => setPreferences(e.target.value)}
            rows={3}
            className={INPUT_CLS}
            placeholder="Describe your reading preferences..."
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2 rounded text-sm font-semibold"
        >
          {loading ? 'Thinking...' : 'Get Recommendations'}
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
