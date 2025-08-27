export default function Header() {
  return (
    <header className="mb-8 text-center space-y-4">
      <div className="relative">
      <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary via-primary/80 to-primary bg-clip-text text-transparent">
          <span className="mr-2 text-primary text-5xl">📰</span>
          <span className="bg-gradient-to-r from-primary via-primary/80 to-primary bg-clip-text text-transparent">
            News Contrast AI
          </span>
      </h1>
        <div className="absolute -inset-1 bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10 blur-lg -z-10 opacity-50"></div>
      </div>

      <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
        Harness the power of AI to verify news authenticity and combat misinformation
      </p>

      <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
        <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
        <span>Real-time fact checking powered by advanced ML</span>
      </div>
    </header>
  );
}
