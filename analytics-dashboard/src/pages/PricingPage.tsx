import { Link } from 'react-router-dom';

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Header */}
      <nav className="fixed top-0 w-full bg-gray-900/80 backdrop-blur-sm z-50 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
              Content Creation
            </Link>
            <div className="hidden md:flex space-x-8">
              <Link to="/" className="text-gray-300 hover:text-white transition">Home</Link>
              <Link to="/pricing" className="text-white font-semibold">Pricing</Link>
              <Link to="/dashboard" className="text-gray-300 hover:text-white transition">Dashboard</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="pt-32 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Start free, upgrade when you need more. No hidden fees.
          </p>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Free Tier */}
            <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700">
              <h3 className="text-2xl font-bold text-white mb-2">Free</h3>
              <div className="text-5xl font-bold text-white mb-6">
                $0<span className="text-xl text-gray-400">/month</span>
              </div>
              <p className="text-gray-400 mb-6">Perfect for trying out the platform</p>
              <ul className="space-y-4 mb-8">
                {[
                  '10 uploads per month',
                  '1 platform (your choice)',
                  'AI caption generation',
                  'Basic analytics',
                  'Community support',
                  'Video processing'
                ].map((feature, idx) => (
                  <li key={idx} className="flex items-start text-gray-300">
                    <span className="text-green-400 mr-3 mt-1">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Link to="/dashboard"
                className="block w-full bg-gray-700 hover:bg-gray-600 text-white py-3 rounded-full font-bold text-center transition">
                Get Started
              </Link>
            </div>

            {/* Pro Tier */}
            <div className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl p-8 transform scale-105 shadow-2xl relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-yellow-400 text-gray-900 px-4 py-1 rounded-full text-sm font-bold">
                MOST POPULAR
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Pro</h3>
              <div className="text-5xl font-bold text-white mb-6">
                $29<span className="text-xl text-purple-200">/month</span>
              </div>
              <p className="text-purple-100 mb-6">For serious content creators</p>
              <ul className="space-y-4 mb-8">
                {[
                  '100 uploads per month',
                  'All 3 platforms',
                  'AI caption generation',
                  'Advanced analytics',
                  'Custom AI prompts',
                  'Priority support',
                  'Scheduled posts',
                  'Video processing'
                ].map((feature, idx) => (
                  <li key={idx} className="flex items-start text-white">
                    <span className="text-yellow-300 mr-3 mt-1">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Link to="/dashboard"
                className="block w-full bg-white hover:bg-gray-100 text-purple-600 py-3 rounded-full font-bold text-center transition">
                Start Pro Trial
              </Link>
            </div>

            {/* Enterprise Tier */}
            <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700">
              <h3 className="text-2xl font-bold text-white mb-2">Enterprise</h3>
              <div className="text-5xl font-bold text-white mb-6">
                $99<span className="text-xl text-gray-400">/month</span>
              </div>
              <p className="text-gray-400 mb-6">For teams and agencies</p>
              <ul className="space-y-4 mb-8">
                {[
                  'Unlimited uploads',
                  'All platforms',
                  'AI caption generation',
                  'Advanced analytics',
                  'Custom integrations',
                  'Dedicated support',
                  'API access',
                  'White-label options',
                  'Team collaboration'
                ].map((feature, idx) => (
                  <li key={idx} className="flex items-start text-gray-300">
                    <span className="text-green-400 mr-3 mt-1">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <a href="mailto:enterprise@contentcreation.app"
                className="block w-full bg-gray-700 hover:bg-gray-600 text-white py-3 rounded-full font-bold text-center transition">
                Contact Sales
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Comparison Table */}
      <div className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Detailed Feature Comparison
          </h2>
          <div className="bg-gray-800 rounded-2xl overflow-hidden border border-gray-700">
            <table className="w-full">
              <thead className="bg-gray-900">
                <tr>
                  <th className="px-6 py-4 text-left text-white font-semibold">Feature</th>
                  <th className="px-6 py-4 text-center text-white font-semibold">Free</th>
                  <th className="px-6 py-4 text-center text-white font-semibold">Pro</th>
                  <th className="px-6 py-4 text-center text-white font-semibold">Enterprise</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {[
                  { feature: 'Uploads per month', free: '10', pro: '100', enterprise: 'Unlimited' },
                  { feature: 'Platforms', free: '1', pro: 'All 3', enterprise: 'All 3 + custom' },
                  { feature: 'AI Caption Generation', free: '✓', pro: '✓', enterprise: '✓ Custom models' },
                  { feature: 'Video Processing', free: '✓ Basic', pro: '✓ Advanced', enterprise: '✓ Priority' },
                  { feature: 'Analytics Dashboard', free: 'Basic', pro: 'Advanced', enterprise: 'Enterprise + exports' },
                  { feature: 'Scheduled Posts', free: '—', pro: '✓', enterprise: '✓' },
                  { feature: 'API Access', free: '—', pro: '—', enterprise: '✓' },
                  { feature: 'Support', free: 'Community', pro: 'Email (48h)', enterprise: 'Dedicated + Phone' }
                ].map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-750 transition">
                    <td className="px-6 py-4 text-gray-300">{row.feature}</td>
                    <td className="px-6 py-4 text-center text-gray-400">{row.free}</td>
                    <td className="px-6 py-4 text-center text-gray-300">{row.pro}</td>
                    <td className="px-6 py-4 text-center text-gray-300">{row.enterprise}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            {[
              {
                q: 'Can I change plans at any time?',
                a: 'Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately, and we\'ll prorate any charges.'
              },
              {
                q: 'What happens when I hit my upload limit?',
                a: 'You\'ll receive a notification at 80% usage. If you hit the limit, you can either wait for the next billing cycle or upgrade to a higher tier.'
              },
              {
                q: 'Is my content secure?',
                a: 'Absolutely. Your videos are processed locally on your machine and never stored on our servers. Only OAuth credentials are encrypted and stored securely in the cloud.'
              },
              {
                q: 'Do you offer refunds?',
                a: 'Yes, we offer a 30-day money-back guarantee for Pro and Enterprise plans. No questions asked.'
              }
            ].map((faq, idx) => (
              <div key={idx} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-bold text-white mb-2">{faq.q}</h3>
                <p className="text-gray-400">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to get started?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of creators automating their content workflow.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/dashboard"
              className="bg-gradient-to-r from-purple-500 to-pink-600 text-white px-8 py-4 rounded-full font-bold text-lg hover:shadow-2xl transition transform hover:-translate-y-1">
              Start Free Trial
            </Link>
            <a href="mailto:enterprise@contentcreation.app"
              className="bg-gray-800 text-white px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-700 transition">
              Contact Sales
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-950 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-gray-400">
              © 2025 Content Creation. All rights reserved.
            </div>
            <div className="flex space-x-6">
              <a href="/terms.html" className="text-gray-400 hover:text-white transition">Terms</a>
              <a href="/privacy.html" className="text-gray-400 hover:text-white transition">Privacy</a>
              <a href="mailto:support@contentcreation.app" className="text-gray-400 hover:text-white transition">Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}



