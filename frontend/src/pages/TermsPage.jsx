import { Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"
import { useEffect } from "react";

export default function TermsPage() {
    useEffect(() => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    }, []);
  return (
    <div className="black">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
        <Link
            to="/"
            className="inline-flex items-center gap-2 text-gray-300 hover:text-white transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <h1 className="text-4xl font-bold mb-4">Terms of Service</h1>
          <p className="text-gray-300">Last updated: December 2024</p>
        </div>

        {/* Content */}
        <div className="prose prose-invert max-w-none">
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                By accessing and using News Contrast AI ("the Service"), you accept and agree to be bound by the terms
                and provision of this agreement. If you do not agree to abide by the above, please do not use this
                service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">2. Description of Service</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                News Contrast AI is an artificial intelligence-powered platform that analyzes news headlines and content
                to help users identify potentially misleading or false information. The Service provides analysis and
                recommendations but should not be considered as the sole source for determining the veracity of news
                content.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">3. User Responsibilities</h2>
              <div className="text-gray-300 leading-relaxed space-y-3">
                <p>You agree to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Use the Service only for lawful purposes</li>
                  <li>Not submit content that is harmful, offensive, or violates any laws</li>
                  <li>Not attempt to reverse engineer or compromise the Service</li>
                  <li>Not use the Service to spread misinformation or false content</li>
                  <li>Respect intellectual property rights</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">4. AI Analysis Disclaimer</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                The AI analysis provided by News Contrast AI is for informational purposes only. While we strive for
                accuracy, the Service may not always correctly identify false or misleading information. Users should:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 text-gray-300">
                <li>Use critical thinking and verify information through multiple sources</li>
                <li>Not rely solely on our analysis for important decisions</li>
                <li>Understand that AI systems can have biases and limitations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">5. Privacy and Data</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Your privacy is important to us. Please review our Privacy Policy to understand how we collect, use, and
                protect your information. By using the Service, you consent to the collection and use of information as
                outlined in our Privacy Policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">6. Intellectual Property</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                The Service and its original content, features, and functionality are and will remain the exclusive
                property of News Contrast AI and its licensors. The Service is protected by copyright, trademark, and
                other laws.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">7. Limitation of Liability</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                In no event shall News Contrast AI, nor its directors, employees, partners, agents, suppliers, or
                affiliates, be liable for any indirect, incidental, special, consequential, or punitive damages,
                including without limitation, loss of profits, data, use, goodwill, or other intangible losses,
                resulting from your use of the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">8. Service Availability</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We reserve the right to withdraw or amend our Service, and any service or material we provide, in our
                sole discretion without notice. We will not be liable if for any reason all or any part of the Service
                is unavailable at any time or for any period.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">9. Termination</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We may terminate or suspend your access immediately, without prior notice or liability, for any reason
                whatsoever, including without limitation if you breach the Terms.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">10. Changes to Terms</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a
                revision is material, we will try to provide at least 30 days notice prior to any new terms taking
                effect.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">11. Contact Information</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                If you have any questions about these Terms of Service, please contact us at:
              </p>
              <div className="bg-[#3a3a3a] p-4 rounded-lg">
                <p className="text-white">Email: moregurpreetsingh@gmail.com</p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
