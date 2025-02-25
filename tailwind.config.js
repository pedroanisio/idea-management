/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'neural-blue': '#1E2A5E',
        'cognitive-white': '#FFFFFF',
        'algorithm-gray': '#F5F7FA',
        'interface-divider': '#E2E8F0',
        'data-text': '#2D3748',
        'intelligence-purple': '#6B46C1',
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms')
  ]
}
