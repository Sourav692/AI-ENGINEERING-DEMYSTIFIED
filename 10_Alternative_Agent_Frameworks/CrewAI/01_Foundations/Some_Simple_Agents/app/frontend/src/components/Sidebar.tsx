import type { PageId } from '../App'

interface Item {
  id: PageId
  label: string
  icon: string
}

const ITEMS: Item[] = [
  { id: 'fitness',      label: 'Fitness Tracker',       icon: '💪' },
  { id: 'travel',       label: 'Travel Advisor',         icon: '✈️' },
  { id: 'images',       label: 'Image Generator',        icon: '🎨' },
  { id: 'books',        label: 'Book Recommender',       icon: '📚' },
  { id: 'data-analyst', label: 'Data Analyst',           icon: '📊' },
  { id: 'fraud',        label: 'Fraud Detector',         icon: '🔍' },
  { id: 'onboarding',   label: 'Employee Onboarding',    icon: '👤' },
  { id: 'summarizer',   label: 'Doc Summarizer',         icon: '📄' },
]

interface Props {
  active: PageId
  onSelect: (id: PageId) => void
}

export default function Sidebar({ active, onSelect }: Props) {
  return (
    <nav className="w-56 shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
      <div className="px-4 py-5 border-b border-gray-800">
        <h1 className="text-sm font-bold text-indigo-400 uppercase tracking-widest">
          CrewAI Hub
        </h1>
      </div>
      <ul className="flex-1 overflow-y-auto py-2">
        {ITEMS.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => onSelect(item.id)}
              className={`w-full text-left px-4 py-3 flex items-center gap-3 text-sm transition-colors ${
                active === item.id
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-100'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  )
}
