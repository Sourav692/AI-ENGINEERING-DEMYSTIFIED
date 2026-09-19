import { useState } from 'react'
import StreamOutput from '../components/StreamOutput'

const DEFAULT_TRANSACTIONS = `TXN1 | Withdrawal | $500 | ATM | New York | 2024-07-01 14:23 | Card Ending: 1234
TXN2 | Online Purchase | $200 | Electronics Store | San Francisco | 2024-07-02 09:45 | IP: 192.168.0.1
TXN3 | Transfer | $1,000 | Bank Account | Zurich | 2024-07-02 17:10 | Beneficiary: John Doe
TXN4 | POS Purchase | $50 | Grocery Store | Berlin | 2024-07-03 12:30 | Card Ending: 5678
TXN5 | Withdrawal | $400 | ATM | Dubai | 2024-07-04 08:15 | Card Ending: 1234
TXN6 | Online Purchase | $150 | Retail Store | Paris | 2024-07-04 20:50 | IP: 10.0.0.2
TXN7 | Transfer | $2,000 | Bank Account | London | 2024-07-05 11:30 | Beneficiary: Jane Smith
TXN11 | Withdrawal | $9,999 | ATM | Las Vegas | 2024-07-07 03:15 | Card Ending: 9999
TXN12 | Transfer | $50,000 | Offshore Account | Cayman Islands | 2024-07-07 05:00 | Beneficiary: Unknown
TXN13 | Online Purchase | $5,500 | Luxury Retailer | Unknown Location | 2024-07-07 23:59 | IP: 255.255.255.0`

const LABEL_CLS = 'block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1'
const INPUT_CLS = 'w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500'

export default function FraudPage() {
  const [transactions, setTransactions] = useState(DEFAULT_TRANSACTIONS)
  const [stream, setStream] = useState<ReadableStream<Uint8Array> | null>(null)
  const [finalResult, setFinalResult] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setFinalResult('')
    setStream(null)

    const transaction_list = transactions.split('\n').map((s) => s.trim()).filter(Boolean)

    const res = await fetch('/api/fraud/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transaction_list }),
    })
    setStream(res.body)
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">Fraud Detector</h1>
      <p className="text-gray-500 text-sm mb-6">
        Analyze transactions for anomalies. Uses ConditionalTask — escalation triggers automatically when &gt;5 anomalies found.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div>
          <label className={LABEL_CLS}>Transactions (one per line)</label>
          <textarea
            value={transactions}
            onChange={(e) => setTransactions(e.target.value)}
            rows={10}
            className={INPUT_CLS + ' font-mono'}
            placeholder="TXN1 | Withdrawal | $500 | ..."
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2 rounded text-sm font-semibold"
        >
          {loading ? 'Detecting...' : 'Detect Fraud'}
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
