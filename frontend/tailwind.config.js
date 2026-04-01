/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                syne: ["'Syne'", "sans-serif"],
                dm: ["'DM Sans'", "sans-serif"],
            },
            colors: {
                // SymptoSense core palette
                ss: {
                    base: "#05080f",
                    surface: "rgba(255,255,255,0.04)",
                    "surface-hover": "rgba(255,255,255,0.08)",
                    teal: "#0ea5e9",
                    violet: "#7c3aed",
                    indigo: "#818cf8",
                    text: "#f0f4ff",
                    muted: "rgba(200,210,240,0.55)",
                },

                // Legacy mapped colors for MUI protected routes
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
                primary: {
                    DEFAULT: "var(--primary)",
                    foreground: "var(--primary-foreground)",
                    50: "var(--primary-50)",
                    100: "var(--primary-100)",
                    200: "var(--primary-200)",
                    400: "var(--primary-400)",
                    500: "var(--primary-500)",
                    600: "var(--primary-600)",
                },
                secondary: {
                    DEFAULT: "var(--secondary)",
                    foreground: "var(--secondary-foreground)",
                },
                muted: {
                    DEFAULT: "var(--muted)",
                    foreground: "var(--muted-foreground)",
                },
                accent: {
                    DEFAULT: "var(--accent)",
                    foreground: "var(--accent-foreground)",
                    blue: "var(--accent-blue)",
                    violet: "var(--accent-violet-legacy)",
                },
                destructive: {
                    DEFAULT: "var(--destructive)",
                    foreground: "var(--destructive-foreground)",
                },
                border: "var(--border)",
                input: "var(--input)",
                ring: "var(--ring)",
                chart: {
                    1: "var(--chart-1)",
                    2: "var(--chart-2)",
                    3: "var(--chart-3)",
                    4: "var(--chart-4)",
                    5: "var(--chart-5)",
                },
                success: "var(--success)",
                warning: "var(--warning)",
                danger: "var(--danger)",
                info: "var(--info)",
                risk: {
                    high: "var(--risk-high)",
                    moderate: "var(--risk-moderate)",
                    low: "var(--risk-low)",
                },
                medical: {
                    clinical: "#2F80ED",
                    ayurveda: "#27AE60",
                    homeopathy: "#9B51E0",
                    lifestyle: "#F2994A",
                },
                surface: {
                    info: "var(--surface-info)",
                    warning: "var(--surface-warning)",
                    disclaimer: "var(--surface-disclaimer)",
                },
            },
            borderRadius: {
                xl: "1rem",
                lg: "0.5rem",
            },
        },
    },
    plugins: [],
}
