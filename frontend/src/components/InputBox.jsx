import { useState } from "react";

export default function InputBox({ onAnalyze, loading }) {
  const [text, setText] = useState("");

  const handleSubmit = () => {
    if (text.trim()) {
      onAnalyze(text);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="relative">
        <textarea
          className="w-full p-4 border border-border rounded-xl placeholder:text-muted-foreground focus:ring-2 focus:ring-ring focus:border-primary focus:outline-none transition-all duration-200 resize-none shadow-sm bg-neutral-800 text-white"
          rows={4}
          placeholder="📝 Paste your news headline or article text here to verify its authenticity..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={handleKeyPress}
          aria-label="News text input for analysis"
        />
        <div className="absolute bottom-3 right-3 text-xs text-muted-foreground">
          Ctrl + Enter to analyze
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {text.length > 0 && (
            <span className="flex items-center gap-2">
              📊 {text.length} characters
              {text.length > 500 && (
                <span className="text-chart-3">• Long text detected</span>
              )}
            </span>
          )}
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading || !text.trim()}
          className="px-8 py-3 font-semibold rounded-xl shadow-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 active:scale-95 text-black bg-white border border-slate-500"
          aria-label={loading ? "Analyzing content" : "Analyze content"}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
              Analyzing...
            </span>
          ) : (
            <span className="flex items-center gap-2">🔍 Analyze Content</span>
          )}
        </button>
      </div>
    </div>
  );
}
