/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        port: {
          bg: '#f8fafc',
          panel: '#ffffff',
          border: '#e2e8f0',
          accent: '#2563eb',
          success: '#16a34a',
          warning: '#d97706',
          danger: '#dc2626',
          muted: '#64748b',
        },
      },
    },
  },
  plugins: [],
};
