/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'app-green': '#1B4332',
        'app-gold': '#C9A84C',
        'app-bg': '#FAFAF7',
      },
    },
  },
  plugins: [],
}

