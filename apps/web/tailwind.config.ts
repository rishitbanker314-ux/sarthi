import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class", '[data-theme="dark"]'],
  content: [
    "./src/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "../../packages/ui/src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: { fontFamily: { sans: ["var(--font-sans)"], serif: ["var(--font-serif)"] },
      colors: {
        border: "var(--border)",
        input: "var(--input)",
        ring: "var(--ring)",
        background: "var(--background)",
        foreground: "var(--foreground)",
        card: {
          DEFAULT: "var(--card)",
          foreground: "var(--card-foreground)",
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)",
        },
        muted: {
          DEFAULT: "var(--muted)",
          foreground: "var(--muted-foreground)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          foreground: "var(--accent-foreground)",
        },
        callout: {
          info: "var(--callout-info)",
          "info-bg": "var(--callout-info-bg)",
          tip: "var(--callout-tip)",
          "tip-bg": "var(--callout-tip-bg)",
          warning: "var(--callout-warning)",
          "warning-bg": "var(--callout-warning-bg)",
          misconception: "var(--callout-misconception)",
          "misconception-bg": "var(--callout-misconception-bg)",
          ai: "var(--callout-ai)",
          "ai-bg": "var(--callout-ai-bg)",
        },
        mastery: {
          1: "var(--mastery-1)",
          2: "var(--mastery-2)",
          3: "var(--mastery-3)",
          4: "var(--mastery-4)",
          5: "var(--mastery-5)",
        }
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}

export default config
