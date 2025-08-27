import { Link } from "react-router-dom";
import { Shield, Zap, Target, Users } from "lucide-react";
// Import your Button and Card components (or use simple HTML tags)
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto max-w-6xl px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary text-primary-foreground rounded-lg flex items-center justify-center font-bold">
                N
              </div>
              <span className="text-xl font-bold">News Contrast AI</span>
            </div>
            <nav className="hidden md:flex items-center space-x-6">
              <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">
                How It Works
              </a>
              <a href="#testimonials" className="text-muted-foreground hover:text-foreground transition-colors">
                Reviews
              </a>
              <Link href="/analyze">
                <Button className="bg-primary text-primary-foreground hover:bg-primary/90">Try It Now</Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 text-balance">
            Detect Fake News
            <span className="block text-primary">Instantly with AI</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto text-pretty">
            Empower your news consumption with advanced AI analysis. Get instant credibility scores and detailed insights for any headline or article.
          </p>
          <div className="flex gap-4 justify-center items-center">
            <Link to="/analyze">
                <button className="bg-primary text-black px-6 py-2 rounded-md hover:bg-primary/90 transition text-base font-medium">
                Start Analyzing
                </button>
            </Link>
            <button className="bg-black text-white px-6 py-2 rounded-md hover:bg-gray-800 transition text-base font-medium">
                Watch Demo
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-card">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful AI Analysis</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our advanced algorithms analyze multiple factors to determine news credibility
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[ 
              { icon: Shield, title: "Real-time Detection", description: "Instant analysis of headlines and articles with advanced AI models" },
              { icon: Zap, title: "Lightning Fast", description: "Get results in seconds with our optimized processing pipeline" },
              { icon: Target, title: "High Accuracy", description: "Trained on millions of verified news articles for precise detection" },
              { icon: Users, title: "Trusted by Thousands", description: "Join journalists, researchers, and informed citizens worldwide" }
            ].map(({ icon: Icon, title, description }, idx) => (
              <Card key={idx} className="border-border bg-background">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-primary/10 text-primary rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{title}</h3>
                  <p className="text-muted-foreground">{description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Simple, fast, and accurate news analysis in three easy steps
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[ 
              { step: 1, title: "Paste Your Text", description: "Copy and paste any news headline or article you want to verify" },
              { step: 2, title: "AI Analysis", description: "Our AI analyzes language patterns, sources, and credibility indicators" },
              { step: 3, title: "Get Results", description: "Receive detailed analysis with credibility score and explanations" }
            ].map(({ step, title, description }) => (
              <div key={step} className="text-center">
                <div className="w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
                  {step}
                </div>
                <h3 className="text-2xl font-semibold mb-4">{title}</h3>
                <p className="text-muted-foreground">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 px-4 bg-card">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Trusted by Professionals</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              See what journalists and researchers say about News Contrast AI
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                initials: "SJ",
                name: "Sarah Johnson",
                role: "Investigative Journalist",
                quote: "This tool has revolutionized how I verify sources. The accuracy is impressive and saves me hours of research.",
              },
              {
                initials: "MC",
                name: "Dr. Michael Chen",
                role: "Media Researcher",
                quote: "Essential for fact-checking in today's information landscape. The detailed analysis helps me understand the reasoning.",
              },
              {
                initials: "ER",
                name: "Emily Rodriguez",
                role: "News Editor",
                quote: "Fast, reliable, and easy to use. It's become an indispensable part of my daily news consumption routine.",
              },
            ].map(({ initials, name, role, quote }, idx) => (
              <Card key={idx} className="border-border bg-background">
                <CardContent className="p-6">
                  <p className="text-muted-foreground mb-4">"{quote}"</p>
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center mr-3">
                      <span className="text-primary font-semibold">{initials}</span>
                    </div>
                    <div>
                      <p className="font-semibold">{name}</p>
                      <p className="text-sm text-muted-foreground">{role}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Fight Misinformation?</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of users who trust News Contrast AI to verify their news sources
          </p>
          <Link to="/analyze">
            <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-4 text-lg">
              Start Analyzing News Now
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-primary text-primary-foreground rounded-lg flex items-center justify-center font-bold">
                N
              </div>
              <span className="text-xl font-bold">News Contrast AI</span>
            </div>
            <div className="flex space-x-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-foreground transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-foreground transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-foreground transition-colors">Contact</a>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
            <p>&copy; 2024 News Contrast AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
