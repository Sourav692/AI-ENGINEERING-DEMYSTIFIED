import { useState } from 'react'
import Sidebar from './components/Sidebar'
import FitnessPage from './pages/FitnessPage'
import TravelPage from './pages/TravelPage'
import ImageGenPage from './pages/ImageGenPage'
import BookPage from './pages/BookPage'
import DataAnalystPage from './pages/DataAnalystPage'
import FraudPage from './pages/FraudPage'
import OnboardingPage from './pages/OnboardingPage'
import SummarizerPage from './pages/SummarizerPage'

export type PageId =
  | 'fitness'
  | 'travel'
  | 'images'
  | 'books'
  | 'data-analyst'
  | 'fraud'
  | 'onboarding'
  | 'summarizer'

const PAGES: Record<PageId, React.ComponentType> = {
  fitness: FitnessPage,
  travel: TravelPage,
  images: ImageGenPage,
  books: BookPage,
  'data-analyst': DataAnalystPage,
  fraud: FraudPage,
  onboarding: OnboardingPage,
  summarizer: SummarizerPage,
}

export default function App() {
  const [active, setActive] = useState<PageId>('fitness')
  const Page = PAGES[active]

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100 overflow-hidden">
      <Sidebar active={active} onSelect={setActive} />
      <main className="flex-1 overflow-y-auto p-8">
        <Page />
      </main>
    </div>
  )
}
