/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0F172A',
        accent: '#1777FF',
        'accent-hover': '#0d5fd6',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
      },
      borderRadius: {
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
      }
    },
  },
  plugins: [],
}
