import { useState } from "react";

export default function InputBox({ onAnalyze, loading }) {
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [inputMode, setInputMode] = useState("text"); // "text" or "url"
  const [includeExplanations, setIncludeExplanations] = useState(true);

  const handleSubmit = () => {
    const options = { includeExplanations };
    
    if (inputMode === "text" && text.trim()) {
      options.text = text.trim();
      onAnalyze(options);
    } else if (inputMode === "url" && url.trim()) {
      options.url = url.trim();
      onAnalyze(options);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      handleSubmit();
    }
  };

  const isValidUrl = (string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  const canSubmit = () => {
    if (inputMode === "text") return text.trim().length > 0;
    if (inputMode === "url") return url.trim().length > 0 && isValidUrl(url.trim());
    return false;
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Input Mode Toggle */}
      <div className="mb-4 flex items-center justify-center gap-2 bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setInputMode("text")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
            inputMode === "text"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          📝 Text Input
        </button>
        <button
          onClick={() => setInputMode("url")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
            inputMode === "url"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          🔗 URL Input
        </button>
      </div>

      {/* Input Area */}
      <div className="relative">
        {inputMode === "text" ? (
          <textarea
            className="w-full p-4 border border-border rounded-xl placeholder:text-muted-foreground focus:ring-2 focus:ring-ring focus:border-primary focus:outline-none transition-all duration-200 resize-none shadow-sm bg-neutral-800 text-white"
            rows={4}
            placeholder="📝 Paste your news headline or article text here to verify its authenticity..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyPress={handleKeyPress}
            aria-label="News text input for analysis"
          />
        ) : (
          <input
            type="url"
            className="w-full p-4 border border-border rounded-xl placeholder:text-muted-foreground focus:ring-2 focus:ring-ring focus:border-primary focus:outline-none transition-all duration-200 shadow-sm bg-neutral-800 text-white"
            placeholder="🔗 Enter a news article URL (e.g., https://example.com/news-article)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            aria-label="News URL input for analysis"
          />
        )}
        <div className="absolute bottom-3 right-3 text-xs text-muted-foreground">
          Ctrl + Enter to analyze
        </div>
      </div>

      {/* Options */}
      <div className="mt-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer">
            <input
              type="checkbox"
              checked={includeExplanations}
              onChange={(e) => setIncludeExplanations(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            📊 Include detailed explanations
          </label>
        </div>
      </div>

      {/* Status and Submit */}
      <div className="mt-4 flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {inputMode === "text" && text.length > 0 && (
            <span className="flex items-center gap-2">
              📊 {text.length} characters
              {text.length > 500 && (
                <span className="text-chart-3">• Long text detected</span>
              )}
            </span>
          )}
          {inputMode === "url" && url.length > 0 && (
            <span className="flex items-center gap-2">
              {isValidUrl(url) ? (
                <span className="text-green-600">✅ Valid URL</span>
              ) : (
                <span className="text-red-600">❌ Invalid URL format</span>
              )}
            </span>
          )}
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading || !canSubmit()}
          className="px-8 py-3 font-semibold rounded-xl shadow-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 active:scale-95 text-black bg-white border border-slate-500"
          aria-label={loading ? "Analyzing content" : "Analyze content"}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
              Analyzing...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              🔍 Analyze {inputMode === "url" ? "URL" : "Content"}
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
