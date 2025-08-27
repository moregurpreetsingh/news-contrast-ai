export default function ResultCard({ result }) {
  if (!result) return null;

  const getStatusColor = (status) => {
    if (status?.toLowerCase().includes("fake") || status?.toLowerCase().includes("false")) {
      return "text-red-600 bg-red-100 border-red-200";
    }
    if (status?.toLowerCase().includes("real") || status?.toLowerCase().includes("true")) {
      return "text-green-600 bg-green-100 border-green-200";
    }
    return "text-yellow-600 bg-yellow-100 border-yellow-200";
  };

  const getMLCheckIcon = (label) => {
    if (label?.toLowerCase().includes("fake")) return "🚨";
    if (label?.toLowerCase().includes("real")) return "✅";
    return "⚠️";
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

        {/* ML Fake News Check */}
        {result.ml_fake_news_check && (
          <div className="border border-gray-200 rounded-xl p-4 bg-white">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">🤖 Machine Learning Analysis</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getMLCheckIcon(result.ml_fake_news_check.label)}</span>
                <span
                  className={`px-4 py-2 rounded-lg text-sm font-medium border ${getStatusColor(
                    result.ml_fake_news_check.label
                  )}`}
                >
                  {result.ml_fake_news_check.label}
                </span>
              </div>
              {result.ml_fake_news_check.reason && (
                <p className="text-gray-600 text-sm ml-8 italic">
                  Reasoning: {result.ml_fake_news_check.reason}
                </p>
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
              </div>
              {result.fact_check.evidence?.headline && (
                <div className="bg-green-50 rounded-lg p-3 border-l-4 border-green-500">
                  <p className="text-sm text-gray-800">
                    <span className="font-medium">Related Evidence:</span> {result.fact_check.evidence.headline}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
