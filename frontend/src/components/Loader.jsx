export default function Loader() {
  return (
    <div className="flex flex-col justify-center items-center mt-8 space-y-4">
      <div className="relative">
        {/* Outer spin */}
        <div className="w-12 h-12 border-4 border-muted border-t-primary rounded-full animate-spin"></div>
        {/* Inner reverse spin */}
        <div className="absolute inset-0 w-12 h-12 border-4 border-transparent border-r-primary/60 rounded-full animate-spin animate-reverse"></div>
      </div>

      <div className="text-center space-y-2">
        <p className="text-muted-foreground font-medium">Analyzing content...</p>
        <div className="flex items-center justify-center space-x-1">
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
          <div
            className="w-2 h-2 bg-primary rounded-full animate-bounce"
            style={{ animationDelay: '0.1s' }}
          ></div>
          <div
            className="w-2 h-2 bg-primary rounded-full animate-bounce"
            style={{ animationDelay: '0.2s' }}
          ></div>
        </div>
      </div>
    </div>
  );
}
