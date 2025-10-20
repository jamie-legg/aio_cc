/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'mono': ['JetBrains Mono', 'monospace'],
      },
      colors: {
        'terminal-red': '#ff0040',
        'terminal-red-light': '#ff4060',
        'terminal-red-dark': '#cc0033',
        'terminal-blue': '#0080ff',
        'terminal-yellow': '#ffff00',
        'terminal-bg': '#0a0a0a',
        'terminal-card': '#1a1a1a',
        gray: {
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
        },
        red: {
          500: '#ef4444',
        },
        pink: {
          500: '#ec4899',
        },
        black: '#000000',
      },
      boxShadow: {
        'brutalist': '8px 8px 0px #ff0040, 16px 16px 0px #0080ff, 24px 24px 0px #ff0040',
        'brutalist-hover': '12px 12px 0px #ff0040, 24px 24px 0px #0080ff, 36px 36px 0px #ff0040',
        'brutalist-button': '4px 4px 0px #ff0040',
        'brutalist-button-hover': '6px 6px 0px #ff0040',
      },
      transform: {
        'perspective-1000': 'perspective(1000px)',
      },
    },
  },
  plugins: [],
}
