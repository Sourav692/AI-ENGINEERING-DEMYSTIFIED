import { useState } from 'react'
import StreamOutput from '../components/StreamOutput'

interface Employee {
  name: string
  start_date: string
  department: string
}

const INPUT_CLS = 'bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500'

const DEFAULT_EMPLOYEES: Employee[] = [
  { name: 'Alice Johnson', start_date: '2024-07-15', department: 'Engineering' },
  { name: 'Bob Smith', start_date: '2024-07-16', department: 'Marketing' },
]

export default function OnboardingPage() {
  const [employees, setEmployees] = useState<Employee[]>(DEFAULT_EMPLOYEES)
  const [stream, setStream] = useState<ReadableStream<Uint8Array> | null>(null)
  const [finalResult, setFinalResult] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (i: number, field: keyof Employee, value: string) => {
    setEmployees((prev) => prev.map((e, idx) => idx === i ? { ...e, [field]: value } : e))
  }

  const addRow = () => setEmployees((prev) => [...prev, { name: '', start_date: '', department: '' }])
  const removeRow = (i: number) => setEmployees((prev) => prev.filter((_, idx) => idx !== i))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setFinalResult('')
    setStream(null)

    const res = await fetch('/api/onboarding/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ employees }),
    })
    setStream(res.body)
  }

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold mb-1">Employee Onboarding</h1>
      <p className="text-gray-500 text-sm mb-6">
        Onboard multiple employees at once: validate start dates, generate email addresses, and produce a summary report.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div className="space-y-2">
          {employees.map((emp, i) => (
            <div key={i} className="flex gap-2 items-center">
              <input
                value={emp.name}
                onChange={(e) => update(i, 'name', e.target.value)}
                placeholder="Full name"
                className={INPUT_CLS + ' flex-1'}
              />
              <input
                type="date"
                value={emp.start_date}
                onChange={(e) => update(i, 'start_date', e.target.value)}
                className={INPUT_CLS + ' w-36'}
              />
              <input
                value={emp.department}
                onChange={(e) => update(i, 'department', e.target.value)}
                placeholder="Department"
                className={INPUT_CLS + ' w-36'}
              />
              <button
                type="button"
                onClick={() => removeRow(i)}
                className="text-gray-500 hover:text-red-400 text-lg px-1"
                title="Remove"
              >
                ×
              </button>
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={addRow}
            className="text-sm text-indigo-400 hover:text-indigo-200 border border-indigo-700 rounded px-3 py-1"
          >
            + Add Employee
          </button>
          <button
            type="submit"
            disabled={loading || employees.length === 0}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2 rounded text-sm font-semibold"
          >
            {loading ? 'Onboarding...' : 'Start Onboarding'}
          </button>
        </div>
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
