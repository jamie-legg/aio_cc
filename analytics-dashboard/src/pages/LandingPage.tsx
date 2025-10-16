import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Header */}
      <nav className="fixed top-0 w-full bg-gray-900/80 backdrop-blur-sm z-50 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
              Content Creation
            </div>
            <div className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-300 hover:text-white transition">Features</a>
              <Link to="/pricing" className="text-gray-300 hover:text-white transition">Pricing</Link>
              <a href="https://api.contentcreation.app/docs" target="_blank" rel="noopener noreferrer" 
                className="text-gray-300 hover:text-white transition">API Docs</a>
              <Link to="/dashboard" className="text-gray-300 hover:text-white transition">Dashboard</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-extrabold text-white mb-6">
            Automate Your
            <span className="block bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
              Social Media Uploads
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto">
            AI-powered captions, multi-platform uploads, and analytics—all from your desktop.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#download" 
              className="bg-gradient-to-r from-purple-500 to-pink-600 text-white px-8 py-4 rounded-full font-bold text-lg hover:shadow-2xl transition transform hover:-translate-y-1">
              Download Free Client
            </a>
            <Link to="/dashboard" 
              className="bg-gray-800 text-white px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-700 transition">
              View Dashboard
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-white mb-16">
            Everything You Need to Automate Content
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: '👁️', title: 'Auto File Watching', desc: 'Drop videos in a folder and let our desktop client handle the rest. No manual uploads needed.' },
              { icon: '🤖', title: 'AI-Powered Captions', desc: 'Generate engaging titles, captions, and hashtags with GPT-4. Optimized for maximum engagement.' },
              { icon: '🚀', title: 'Multi-Platform Upload', desc: 'Upload to Instagram Reels, YouTube Shorts, and TikTok simultaneously with one click.' },
              { icon: '📊', title: 'Real-Time Analytics', desc: 'Track views, likes, and engagement across all platforms in one beautiful dashboard.' },
              { icon: '🎬', title: 'Video Processing', desc: 'Automatic aspect ratio conversion to 9:16, audio mixing, and fade effects—all done locally.' },
              { icon: '🔒', title: 'Secure & Private', desc: 'Your videos stay on your machine. OAuth tokens stored securely in the cloud, encrypted.' }
            ].map((feature, idx) => (
              <div key={idx} 
                className="bg-gray-800 p-8 rounded-2xl hover:bg-gray-750 transition transform hover:-translate-y-2 border border-gray-700">
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pricing Teaser */}
      <div className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Simple, Transparent Pricing</h2>
          <p className="text-xl text-gray-300 mb-10">Start free, upgrade when you need more. No hidden fees.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              { name: 'Free', price: '$0', features: ['10 uploads/month', '1 platform', 'AI captions', 'Basic analytics'] },
              { name: 'Pro', price: '$29', features: ['100 uploads/month', 'All 3 platforms', 'Advanced analytics', 'Priority support'], featured: true },
              { name: 'Enterprise', price: '$99', features: ['Unlimited uploads', 'All platforms', 'API access', 'Dedicated support'] }
            ].map((plan, idx) => (
              <div key={idx} 
                className={`p-8 rounded-2xl ${plan.featured ? 'bg-gradient-to-br from-purple-600 to-pink-600 transform scale-105' : 'bg-gray-800 border border-gray-700'}`}>
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <div className="text-4xl font-bold text-white mb-6">{plan.price}<span className="text-lg">/mo</span></div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="text-gray-300 flex items-center">
                      <span className="mr-2">✓</span> {feature}
                    </li>
                  ))}
                </ul>
                <Link to="/pricing" 
                  className={`block w-full py-3 rounded-full font-bold transition ${
                    plan.featured 
                      ? 'bg-white text-purple-600 hover:bg-gray-100' 
                      : 'bg-gray-700 text-white hover:bg-gray-600'
                  }`}>
                  {plan.featured ? 'Get Started' : 'Learn More'}
                </Link>
              </div>
            ))}
          </div>
          <div className="mt-12">
            <Link to="/pricing" className="text-purple-400 hover:text-purple-300 font-semibold">
              View full pricing comparison →
            </Link>
          </div>
        </div>
      </div>

      {/* Download Section */}
      <div id="download" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Automate Your Content?</h2>
          <p className="text-xl text-gray-300 mb-10">Download the desktop client and start uploading in minutes.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { os: 'macOS', icon: '🍎', file: 'content-creation-macos.dmg' },
              { os: 'Windows', icon: '🪟', file: 'content-creation-windows.exe' },
              { os: 'Linux', icon: '🐧', file: 'content-creation-linux.AppImage' }
            ].map((download, idx) => (
              <a key={idx} href={`#${download.file}`}
                className="bg-gray-800 p-8 rounded-2xl hover:bg-gray-750 transition transform hover:-translate-y-2 border border-gray-700 block">
                <div className="text-5xl mb-4">{download.icon}</div>
                <h3 className="text-xl font-bold text-white mb-2">Download for {download.os}</h3>
                <p className="text-gray-400 text-sm">{download.file}</p>
              </a>
            ))}
          </div>
          <p className="text-gray-400 mt-8">
            Open source client • No credit card required • Free tier forever
          </p>
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
              <a href="https://github.com/yourusername/content-creation" target="_blank" rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition">GitHub</a>
              <a href="mailto:support@contentcreation.app" className="text-gray-400 hover:text-white transition">Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}



