/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F17',
        surface: '#151C28',
        'surface-elevated': '#1F293D',
        border: '#2A364F',
        brand: {
          50: '#EEF6FF',
          100: '#D9ECFF',
          500: '#0066FF',
          600: '#0052CC',
          700: '#003D99',
        },
        tactical: {
          amber: '#F59E0B',
          red: '#EF4444',
          green: '#10B981',
          cyan: '#06B6D4',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
