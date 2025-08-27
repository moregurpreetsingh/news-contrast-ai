import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useEffect } from "react";

export default function PrivacyPage() {
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
          <h1 className="text-4xl font-bold mb-4">Privacy Policy</h1>
          <p className="text-gray-300">Last updated: December 2024</p>
        </div>

        {/* Content */}
        <div className="prose prose-invert max-w-none">
          <div className="space-y-8">
            {/* 1. Information We Collect */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
              <div className="text-gray-300 leading-relaxed space-y-4">
                <h3 className="text-xl font-medium text-white">Information You Provide</h3>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>News headlines and content you submit for analysis</li>
                  <li>Contact information when you reach out to us</li>
                  <li>Feedback and communications you send to us</li>
                </ul>

                <h3 className="text-xl font-medium text-white">Automatically Collected Information</h3>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Usage data and analytics about how you interact with our Service</li>
                  <li>Device information, browser type, and IP address</li>
                  <li>Cookies and similar tracking technologies</li>
                </ul>
              </div>
            </section>

            {/* 2. How We Use Your Information */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
              <div className="text-gray-300 leading-relaxed">
                <p className="mb-4">We use the information we collect to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Provide and improve our AI-powered news analysis service</li>
                  <li>Train and enhance our machine learning models</li>
                  <li>Respond to your inquiries and provide customer support</li>
                  <li>Monitor and analyze usage patterns to improve user experience</li>
                  <li>Detect and prevent fraud, abuse, or security issues</li>
                  <li>Comply with legal obligations and enforce our terms</li>
                </ul>
              </div>
            </section>

            {/* 3. Information Sharing and Disclosure */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">3. Information Sharing and Disclosure</h2>
              <div className="text-gray-300 leading-relaxed space-y-4">
                <p>
                  We do not sell, trade, or rent your personal information to third parties. We may share information in
                  the following circumstances:
                </p>

                <h3 className="text-xl font-medium text-white">Service Providers</h3>
                <p>
                  We may share information with trusted third-party service providers who assist us in operating our
                  Service, such as cloud hosting, analytics, and customer support platforms.
                </p>

                <h3 className="text-xl font-medium text-white">Legal Requirements</h3>
                <p>
                  We may disclose information if required by law, court order, or government request, or to protect our
                  rights, property, or safety.
                </p>

                <h3 className="text-xl font-medium text-white">Business Transfers</h3>
                <p>
                  In the event of a merger, acquisition, or sale of assets, your information may be transferred as part
                  of that transaction.
                </p>
              </div>
            </section>

            {/* 4. Data Security */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">4. Data Security</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We implement appropriate technical and organizational security measures to protect your information
                against unauthorized access, alteration, disclosure, or destruction. However, no method of transmission
                over the internet or electronic storage is 100% secure.
              </p>
              <div className="bg-[#3a3a3a] p-4 rounded-lg">
                <h3 className="text-lg font-medium text-white mb-2">Security Measures Include:</h3>
                <ul className="list-disc list-inside space-y-1 text-gray-300">
                  <li>Encryption of data in transit and at rest</li>
                  <li>Regular security audits and monitoring</li>
                  <li>Access controls and authentication</li>
                  <li>Secure data centers and infrastructure</li>
                </ul>
              </div>
            </section>

            {/* 5. Data Retention */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">5. Data Retention</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We retain your information for as long as necessary to provide our services and fulfill the purposes
                outlined in this Privacy Policy. We may retain certain information for longer periods as required by law
                or for legitimate business purposes.
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 text-gray-300">
                <li>Submitted content: Retained for model training and service improvement</li>
                <li>Usage analytics: Retained for up to 2 years</li>
                <li>Contact information: Retained until you request deletion</li>
              </ul>
            </section>

            {/* 6. Your Rights and Choices */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">6. Your Rights and Choices</h2>
              <div className="text-gray-300 leading-relaxed space-y-4">
                <p>Depending on your location, you may have certain rights regarding your personal information:</p>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-[#3a3a3a] p-4 rounded-lg">
                    <h3 className="text-lg font-medium text-white mb-2">Access & Portability</h3>
                    <p className="text-sm">
                      Request access to your personal information and receive a copy in a portable format.
                    </p>
                  </div>

                  <div className="bg-[#3a3a3a] p-4 rounded-lg">
                    <h3 className="text-lg font-medium text-white mb-2">Correction</h3>
                    <p className="text-sm">Request correction of inaccurate or incomplete personal information.</p>
                  </div>

                  <div className="bg-[#3a3a3a] p-4 rounded-lg">
                    <h3 className="text-lg font-medium text-white mb-2">Deletion</h3>
                    <p className="text-sm">
                      Request deletion of your personal information, subject to certain exceptions.
                    </p>
                  </div>

                  <div className="bg-[#3a3a3a] p-4 rounded-lg">
                    <h3 className="text-lg font-medium text-white mb-2">Opt-out</h3>
                    <p className="text-sm">
                      Opt-out of certain data processing activities or marketing communications.
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* 7. Cookies and Tracking */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">7. Cookies and Tracking</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We use cookies and similar technologies to enhance your experience, analyze usage, and provide
                personalized content. You can control cookie settings through your browser preferences.
              </p>
              <div className="bg-[#3a3a3a] p-4 rounded-lg">
                <h3 className="text-lg font-medium text-white mb-2">Types of Cookies We Use:</h3>
                <ul className="list-disc list-inside space-y-1 text-gray-300 text-sm">
                  <li>Essential cookies for basic functionality</li>
                  <li>Analytics cookies to understand usage patterns</li>
                  <li>Performance cookies to optimize the service</li>
                </ul>
              </div>
            </section>

            {/* 8. International Data Transfers */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">8. International Data Transfers</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Your information may be transferred to and processed in countries other than your own. We ensure
                appropriate safeguards are in place to protect your information in accordance with this Privacy Policy.
              </p>
            </section>

            {/* 9. Children's Privacy */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">9. Children's Privacy</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Our Service is not intended for children under 13 years of age. We do not knowingly collect personal
                information from children under 13. If you become aware that a child has provided us with personal
                information, please contact us.
              </p>
            </section>

            {/* 10. Changes to This Privacy Policy */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">10. Changes to This Privacy Policy</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We may update this Privacy Policy from time to time. We will notify you of any changes by posting the
                new Privacy Policy on this page and updating the "Last updated" date. We encourage you to review this
                Privacy Policy periodically.
              </p>
            </section>

            {/* 11. Contact Us */}
            <section>
              <h2 className="text-2xl font-semibold mb-4">11. Contact Us</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                If you have any questions about this Privacy Policy or our privacy practices, please contact us:
              </p>
              <div className="bg-[#3a3a3a] p-4 rounded-lg space-y-2">
                <p className="text-white">Email: moregurpreetsingh@gmail.com</p>
                <p className="text-white">Subject: Privacy Policy Inquiry</p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
