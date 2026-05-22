import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'ises-green': '#A2D123',
        'forest-green': '#153426',
        primary: '#4d6700',
        error: '#ef4444',
        'error-container': '#fee2e2',
        'on-error-container': '#93000a',
        outline: '#D1D5DB',
        'outline-variant': '#E5E7EB',
        'on-surface': '#111827',
        'on-surface-variant': '#6b7280',
        'on-background': '#111827',
        surface: '#ffffff',
        background: '#F4F7F6',
        canvas: '#F4F7F6',
        'canvas-muted': '#EEF2F1',
      },
      borderRadius: {
        xl: '12px',
        '2xl': '16px',
      },
      boxShadow: {
        soft: '0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.03)',
        'soft-md': '0 2px 8px rgba(0, 0, 0, 0.05), 0 8px 20px rgba(0, 0, 0, 0.04)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [forms],
};
