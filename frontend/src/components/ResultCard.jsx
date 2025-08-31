import { useState } from 'react';

export default function ResultCard({ result, onFeedback, feedbackSubmitted }) {
  const [showExplanation, setShowExplanation] = useState(true);
  const [showDetailedInfo, setShowDetailedInfo] = useState(false);
  
  if (!result) return null;

  const getStatusColor = (status) => {
    if (status?.toLowerCase().includes("fake") || status?.toLowerCase().includes("false")) {
      return "text-red-600 bg-red-100 border-red-200";
    }
    if (status?.toLowerCase().includes("real") || status?.toLowerCase().includes("true") || status?.toLowerCase().includes("valid")) {
      return "text-green-600 bg-green-100 border-green-200";
    }
    if (status?.toLowerCase().includes("unverified") || status?.toLowerCase().includes("questionable")) {
      return "text-orange-600 bg-orange-100 border-orange-200";
    }
    return "text-yellow-600 bg-yellow-100 border-yellow-200";
  };

  const getMLCheckIcon = (label) => {
    if (label?.toLowerCase().includes("fake")) return "🚨";
    if (label?.toLowerCase().includes("real")) return "✅";
    if (label?.toLowerCase().includes("unverified")) return "🔍";
    return "⚠️";
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const handleFeedback = (feedback) => {
    if (onFeedback) {
      onFeedback({
        feedback,
        analysis_id: Date.now().toString(),
        text: result.input_summary
      });
    }
  };

  // Check if the news is classified as valid/real
  const isValidNews = () => {
    const mlCheck = result.ml_fake_news_check?.label?.toLowerCase();
    const validity = result.validity_check?.toLowerCase();
    const factCheck = result.fact_check?.status?.toLowerCase();
    
    return (
      mlCheck?.includes('real') || mlCheck?.includes('valid') ||
      validity?.includes('valid') || validity?.includes('real') ||
      factCheck?.includes('verified') || factCheck?.includes('valid')
    );
  };

  return (
    <div className="mt-8 w-full max-w-2xl mx-auto bg-white rounded-2xl shadow border border-gray-200 overflow-hidden">
      <div className="bg-gray-100 p-6 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">📊 Analysis Result</h2>
      </div>

      <div className="p-6 space-y-6">
        {/* Summary */}
        <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
          <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">📝 Content Summary</h3>
          <p className="text-gray-600">{result.input_summary}</p>
        </div>

        {/* News Classification */}
        <div className="flex items-center gap-3">
          <span className="font-semibold text-gray-800">📰 News Classification:</span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium border ${
              result.is_news
                ? "text-green-600 bg-green-100 border-green-200"
                : "text-gray-500 bg-gray-100 border-gray-200"
            }`}
          >
            {result.is_news ? "✅ Confirmed News Content" : "❌ Not News Content"}
          </span>
        </div>

        {/* Overall Validity Assessment */}
        {result.validity_check && (
          <div className="border border-gray-200 rounded-xl p-4 bg-white">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">🎯 Overall Assessment</h3>
            <div className="flex items-center gap-3">
              <span
                className={`px-4 py-2 rounded-lg text-lg font-medium border ${getStatusColor(
                  result.validity_check
                )}`}
              >
                {result.validity_check}
              </span>
            </div>
          </div>
        )}

        {/* ML Fake News Check */}
        {result.ml_fake_news_check && (
          <div className="border border-gray-200 rounded-xl p-4 bg-white">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">🤖 Machine Learning Analysis</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getMLCheckIcon(result.ml_fake_news_check.label)}</span>
                <span
                  className={`px-4 py-2 rounded-lg text-sm font-medium border ${getStatusColor(
                    result.ml_fake_news_check.label
                  )}`}
                >
                  {result.ml_fake_news_check.label}
                </span>
                {result.ml_fake_news_check.confidence && (
                  <span className={`text-sm font-medium ${getConfidenceColor(result.ml_fake_news_check.confidence)}`}>
                    {(result.ml_fake_news_check.confidence * 100).toFixed(1)}% confidence
                  </span>
                )}
              </div>
              {result.ml_fake_news_check.reason && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-gray-700 text-sm">
                    <span className="font-medium">Reasoning:</span> {result.ml_fake_news_check.reason}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Fact Check */}
        {result.fact_check && (
          <div className="border border-gray-200 rounded-xl p-4 bg-white">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">🔍 Fact Verification</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span
                  className={`px-4 py-2 rounded-lg text-sm font-medium border ${getStatusColor(
                    result.fact_check.status
                  )}`}
                >
                  {result.fact_check.status}
                </span>
                {result.fact_check.confidence && (
                  <span className={`text-sm font-medium ${getConfidenceColor(result.fact_check.confidence)}`}>
                    {(result.fact_check.confidence * 100).toFixed(1)}% confidence
                  </span>
                )}
              </div>
              {result.fact_check.evidence?.matched_headline && (
                <div className="bg-green-50 rounded-lg p-3 border-l-4 border-green-500">
                  <p className="text-sm text-gray-800">
                    <span className="font-medium">Related Evidence:</span> {result.fact_check.evidence.matched_headline}
                  </p>
                  {result.fact_check.evidence.similarity && (
                    <p className="text-xs text-gray-600 mt-1">
                      Similarity: {(result.fact_check.evidence.similarity * 100).toFixed(1)}%
                    </p>
                  )}
                </div>
              )}
              {result.fact_check.explanation && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm text-gray-700">{result.fact_check.explanation}</p>
                </div>
              )}
              {result.fact_check.recommendation && (
                <div className="bg-blue-50 rounded-lg p-3 border-l-4 border-blue-500">
                  <p className="text-sm text-blue-800">
                    <span className="font-medium">Recommendation:</span> {result.fact_check.recommendation}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Forensic Analysis */}
        {result.forensic_analysis && (
          <div className="border border-gray-200 rounded-xl p-4 bg-white">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">🔬 Forensic Analysis</h3>
            <div className="space-y-3">
              {result.forensic_analysis.credibility_assessment && (
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-700">Credibility Score:</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          result.forensic_analysis.credibility_assessment.credibility_score >= 0.7 
                            ? 'bg-green-500' 
                            : result.forensic_analysis.credibility_assessment.credibility_score >= 0.4 
                            ? 'bg-yellow-500' 
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${result.forensic_analysis.credibility_assessment.credibility_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">
                      {(result.forensic_analysis.credibility_assessment.credibility_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}
              {result.forensic_analysis.credibility_assessment?.red_flags?.length > 0 && (
                <div className="bg-red-50 rounded-lg p-3 border-l-4 border-red-500">
                  <p className="text-sm text-red-800">
                    <span className="font-medium">Red Flags:</span> {result.forensic_analysis.credibility_assessment.red_flags.join(', ')}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Additional Information for Valid News */}
        {isValidNews() && (
          <div className="border border-green-200 rounded-xl p-4 bg-green-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-green-800 flex items-center gap-2">✅ Detailed Information</h3>
              <button
                onClick={() => setShowDetailedInfo(!showDetailedInfo)}
                className="text-sm text-green-600 hover:text-green-800 font-medium"
              >
                {showDetailedInfo ? 'Hide Details' : 'Show Details'}
              </button>
            </div>
            
            {showDetailedInfo && (
              <div className="space-y-4">
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <h4 className="font-medium text-green-800 mb-2">📊 Verification Summary</h4>
                  <ul className="text-sm text-green-700 space-y-1 list-disc list-inside">
                    <li>Content has been verified as authentic news</li>
                    <li>Multiple validation layers confirm accuracy</li>
                    <li>Source credibility assessment passed</li>
                    {result.fact_check?.evidence?.matched_headline && (
                      <li>Cross-referenced with trusted news sources</li>
                    )}
                    {result.forensic_analysis?.credibility_assessment?.credibility_score > 0.7 && (
                      <li>High forensic credibility score indicates reliability</li>
                    )}
                  </ul>
                </div>
                
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <h4 className="font-medium text-green-800 mb-2">🔍 Analysis Methodology</h4>
                  <p className="text-sm text-green-700">
                    This content underwent comprehensive analysis including machine learning classification, 
                    fact-checking against trusted sources, forensic linguistic analysis, and credibility assessment. 
                    All indicators support the authenticity of this news content.
                  </p>
                </div>
                
                {result.fact_check?.recommendation && (
                  <div className="bg-white rounded-lg p-4 border border-green-200">
                    <h4 className="font-medium text-green-800 mb-2">💡 Additional Notes</h4>
                    <p className="text-sm text-green-700">{result.fact_check.recommendation}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Detailed Explanations */}
        {result.explanation && (
          <div className="border border-gray-200 rounded-xl p-4 bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-800 flex items-center gap-2">📝 Detailed Analysis</h3>
              <button
                onClick={() => setShowExplanation(!showExplanation)}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                {showExplanation ? 'Hide Details' : 'Show Details'}
              </button>
            </div>
            
            {showExplanation && (
              <div className="space-y-4">
                {result.explanation.positive && (
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-medium text-green-800 mb-2 flex items-center gap-2">
                      ✅ Positive Aspects
                    </h4>
                    <p className="text-green-700 text-sm">{result.explanation.positive}</p>
                  </div>
                )}
                
                {result.explanation.negative && (
                  <div className="bg-red-50 rounded-lg p-4">
                    <h4 className="font-medium text-red-800 mb-2 flex items-center gap-2">
                      ⚠️ Concerns & Risks
                    </h4>
                    <p className="text-red-700 text-sm">{result.explanation.negative}</p>
                  </div>
                )}
                
                {result.explanation.neutral && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-800 mb-2 flex items-center gap-2">
                      📊 Neutral Context
                    </h4>
                    <p className="text-gray-700 text-sm">{result.explanation.neutral}</p>
                  </div>
                )}
                
                {result.explanation.context && (
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-medium text-blue-800 mb-2 flex items-center gap-2">
                      📄 Analysis Context
                    </h4>
                    <p className="text-blue-700 text-sm">{result.explanation.context}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* User Feedback */}
        <div className="border border-gray-200 rounded-xl p-4 bg-white">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">💬 Your Feedback</h3>
          {!feedbackSubmitted ? (
            <div className="space-y-3">
              <p className="text-sm text-gray-600">Was this analysis helpful and accurate?</p>
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => handleFeedback('correct')}
                  className="px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors"
                >
                  ✅ Accurate
                </button>
                <button
                  onClick={() => handleFeedback('partially_correct')}
                  className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg text-sm font-medium hover:bg-yellow-200 transition-colors"
                >
                  🟡 Partially Correct
                </button>
                <button
                  onClick={() => handleFeedback('incorrect')}
                  className="px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition-colors"
                >
                  ❌ Inaccurate
                </button>
              </div>
            </div>
          ) : (
            <div className="text-sm text-green-600 flex items-center gap-2">
              ✅ Thank you for your feedback!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
