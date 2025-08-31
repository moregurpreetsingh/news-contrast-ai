import { Routes, Route } from 'react-router-dom'
import AnalyzePage from './pages/AnalyzePage'
import LandingPage from './pages/LandingPage'
import PrivacyPage from './pages/PrivacyPage'
import TermsPage from './pages/TermsPage'
import StatusPage from './pages/StatusPage'

export default function App() {
  return (
      <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/status" element={<StatusPage />} />
      </Routes>
  )
}
