/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'hsl(var(--color-primary) / <alpha-value>)',
          dark: 'hsl(var(--color-primary-dark) / <alpha-value>)',
        },
        secondary: 'hsl(var(--color-secondary) / <alpha-value>)',
        accent: 'hsl(var(--color-accent) / <alpha-value>)',
        success: 'hsl(var(--color-success) / <alpha-value>)',
        warning: 'hsl(var(--color-warning) / <alpha-value>)',
        danger: 'hsl(var(--color-danger) / <alpha-value>)',
        info: 'hsl(var(--color-info) / <alpha-value>)',
        background: 'hsl(var(--color-bg) / <alpha-value>)',
        'background-alt': 'hsl(var(--color-bg-alt) / <alpha-value>)',
        surface: 'hsl(var(--color-surface) / <alpha-value>)',
        border: 'hsl(var(--color-border) / <alpha-value>)',
        muted: 'hsl(var(--color-muted) / <alpha-value>)',
        foreground: 'hsl(var(--color-foreground) / <alpha-value>)',
        'foreground-muted': 'hsl(var(--color-foreground-muted) / <alpha-value>)',
        code: 'hsl(var(--color-code) / <alpha-value>)',
      },
      fontFamily: {
        sans: [
          'Inter',
          'Lexend',
          'system-ui',
          'sans-serif',
        ],
        mono: [
          'JetBrains Mono',
          'Menlo',
          'monospace',
        ],
      },
      borderRadius: {
        base: 'var(--radius)',
      },
      boxShadow: {
        base: 'var(--shadow)',
        lg: 'var(--shadow-lg)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 3s ease-in-out infinite',
        'fade-in': 'fade-in 0.3s ease-out',
        'zoom-in': 'zoom-in 0.3s ease-out',
        'zoom-in-50': 'zoom-in-50 0.3s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'zoom-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'zoom-in-50': {
          '0%': { transform: 'scale(0.5)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}