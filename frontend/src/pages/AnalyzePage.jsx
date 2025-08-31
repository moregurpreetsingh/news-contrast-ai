import { useState, useRef } from 'react'
import Header from '../components/Header'
import InputBox from '../components/InputBox'
import ResultCard from '../components/ResultCard'
import apiService from '../services/api'
import { ToastContainer, useToasts } from '../components/Toast'

export default function AnalyzePage() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  
  const { toasts, removeToast, showSuccess, showError, showInfo } = useToasts()
  const resultRef = useRef(null)

  const analyzeContent = async (options) => {
    setLoading(true)
    setResult(null)
    setError(null)
    setFeedbackSubmitted(false) // Reset feedback state for new search
    
    showInfo('Analyzing content... This may take a moment.')

    try {
      const data = await apiService.analyzeContent(options)
      setResult(data.text_analysis || data.url_analysis || data)
      showSuccess('Analysis completed successfully!')
      
      // Scroll to results after a brief delay
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start',
          inline: 'nearest'
        })
      }, 300)
      
    } catch (err) {
      console.error('Analysis Error:', err)
      const errorMsg = err.message || 'Analysis failed. Please try again.'
      setError(errorMsg)
      showError(`Analysis failed: ${errorMsg}`, 6000)
    } finally {
      setLoading(false)
    }
  }

  const handleFeedback = async (feedbackData) => {
    try {
      await apiService.submitFeedback({
        text: feedbackData.text,
        analysis_id: feedbackData.analysis_id,
        user_feedback: feedbackData.feedback
      })
      setFeedbackSubmitted(true)
      showSuccess('Thank you for your feedback! It will help improve our system.')
      console.log('Feedback submitted successfully')
    } catch (err) {
      console.error('Feedback Error:', err)
      showError('Failed to submit feedback. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header - Fixed at top */}
      <div className="w-full">
        <Header />
      </div>
      
      {/* Main Content - Centralized */}
      <div className="flex flex-col items-center justify-start px-4 pb-8">
        <div className="w-full max-w-4xl mx-auto">
          {/* Input Section */}
          <div className="mb-8">
            <InputBox onAnalyze={analyzeContent} loading={loading} />
          </div>
          
          {/* Error Section */}
          {error && (
            <div className="mb-6 w-full max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <span className="text-red-600 text-lg">⚠️</span>
                <p className="text-red-800 font-medium">Analysis Error</p>
              </div>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          )}
          
          {/* Results Section */}
          <div ref={resultRef}>
            <ResultCard 
              result={result} 
              onFeedback={handleFeedback} 
              feedbackSubmitted={feedbackSubmitted}
            />
          </div>
        </div>
      </div>
      
      {/* Toast Container */}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  )
}
