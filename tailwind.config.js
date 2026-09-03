/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef7ff',
          100: '#d9edff',
          200: '#bce0ff',
          300: '#8ecdff',
          400: '#59b0ff',
          500: '#338bff',
          600: '#1a6af5',
          700: '#1354e1',
          800: '#1644b6',
          900: '#183d8f',
          950: '#142757',
        },
        fintech: {
          teal: '#0d9488',
          emerald: '#059669',
          amber: '#d97706',
          slate: '#334155',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
