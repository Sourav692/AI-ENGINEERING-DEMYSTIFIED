import { useState } from 'react'
import StreamOutput from '../components/StreamOutput'

const INPUT_CLS = 'w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500'
const LABEL_CLS = 'block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1'

export default function FitnessPage() {
  const [fitnessGoal, setFitnessGoal] = useState('muscle gain')
  const [nutritionPref, setNutritionPref] = useState('high protein')
  const [weightData, setWeightData] = useState('87kg, 85kg, 88kg, 87kg, 86kg')
  const [stream, setStream] = useState<ReadableStream<Uint8Array> | null>(null)
  const [finalResult, setFinalResult] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setFinalResult('')
    setStream(null)

    const res = await fetch('/api/fitness/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fitness_goal: fitnessGoal,
        nutrition_preference: nutritionPref,
        historical_weight_data: weightData.split(',').map((s) => s.trim()).filter(Boolean),
      }),
    })
    setStream(res.body)
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">Fitness Tracker</h1>
      <p className="text-gray-500 text-sm mb-6">Set a goal and get a personalized workout + nutrition plan.</p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div>
          <label className={LABEL_CLS}>Fitness Goal</label>
          <input value={fitnessGoal} onChange={(e) => setFitnessGoal(e.target.value)} className={INPUT_CLS} placeholder="e.g. muscle gain" />
        </div>
        <div>
          <label className={LABEL_CLS}>Nutrition Preference</label>
          <input value={nutritionPref} onChange={(e) => setNutritionPref(e.target.value)} className={INPUT_CLS} placeholder="e.g. high protein" />
        </div>
        <div>
          <label className={LABEL_CLS}>Weight History (comma-separated)</label>
          <input value={weightData} onChange={(e) => setWeightData(e.target.value)} className={INPUT_CLS} placeholder="87kg, 85kg, 88kg" />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2 rounded text-sm font-semibold"
        >
          {loading ? 'Running...' : 'Run Crew'}
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
