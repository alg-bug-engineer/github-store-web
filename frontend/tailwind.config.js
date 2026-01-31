/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Base colors
        'bg-primary': 'var(--bg-primary)',
        'bg-secondary': 'var(--bg-secondary)',
        'bg-tertiary': 'var(--bg-tertiary)',
        'accent-primary': 'var(--accent-primary)',
        'accent-secondary': 'var(--accent-secondary)',
        'accent-tertiary': 'var(--accent-tertiary)',
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-tertiary': 'var(--text-tertiary)',
        'border-default': 'var(--border-default)',
        'border-hover': 'var(--border-hover)',
        // Label colors
        'label-purple': 'var(--label-purple)',
        'label-green': 'var(--label-green)',
        'label-blue': 'var(--label-blue)',
        'label-orange': 'var(--label-orange)',
        'label-gray': 'var(--label-gray)',
        // Header Specific
        'header-bg': 'var(--header-bg)',
        'header-text': 'var(--header-text)',
      },
    },
  },
  plugins: [],
}