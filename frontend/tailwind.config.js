/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: "var(--color-brand)",
        surface: "var(--color-surface)",
        panel: "var(--color-panel)",
        text: "var(--color-text)",
        muted: "var(--color-muted)",
        border: "var(--color-border)",
        high: "var(--color-high)",
        medium: "var(--color-medium)",
        low: "var(--color-low)",
        success: "var(--color-success)"
      },
      boxShadow: {
        soft: "0 18px 48px rgba(10, 32, 54, 0.10)"
      }
    }
  },
  plugins: []
};
