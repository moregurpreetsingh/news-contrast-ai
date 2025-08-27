import { useState } from 'react'
import Header from '../components/Header'
import InputBox from '../components/InputBox'
import ResultCard from '../components/ResultCard'
import Loader from '../components/Loader'

export default function AnalyzePage() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const analyzeText = async (text) => {
    setLoading(true)
    setResult(null)

    try {
      const res = await fetch('http://127.0.0.1:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })

      const data = await res.json()
      setResult(data.text_analysis)
    } catch (err) {
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground px-4">
      <Header />
      <InputBox onAnalyze={analyzeText} loading={loading} />
      {loading && <Loader />}
      <ResultCard result={result} />
    </div>
  )
}
