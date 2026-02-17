/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: "class", // Enable class-based dark mode
    theme: {
        extend: {
            colors: {
                // Map Tailwind colors to CSS variables
                bg: {
                    app: "var(--bg-app)",
                    soft: "var(--bg-soft)",
                    card: "var(--bg-card)",
                },
                text: {
                    primary: "var(--text-primary)",
                    secondary: "var(--text-secondary)",
                    muted: "var(--text-muted)",
                },
                border: {
                    DEFAULT: "var(--border)",
                    soft: "var(--border-soft)",
                },

                // Brand & Status
                primary: {
                    50: "var(--primary-50)",
                    100: "var(--primary-100)",
                    200: "var(--primary-200)",
                    400: "var(--primary-400)",
                    500: "var(--primary-500)",
                    600: "var(--primary-600)",
                    DEFAULT: "var(--primary-500)",
                },
                success: "var(--success)",
                warning: "var(--warning)",
                danger: "var(--danger)",
                info: "var(--info)",

                // Risk Levels
                risk: {
                    high: "var(--risk-high)",
                    moderate: "var(--risk-moderate)",
                    low: "var(--risk-low)",
                },

                // Medical Categories
                medical: {
                    clinical: "#2F80ED", // Keep hex for specific medical references if needed, or map to var
                    ayurveda: "#27AE60",
                    homeopathy: "#9B51E0",
                    lifestyle: "#F2994A",
                },

                // Surface States
                surface: {
                    info: "var(--surface-info)",
                    warning: "var(--surface-warning)",
                    disclaimer: "var(--surface-disclaimer)",
                },
            },
            // Extend borderRadius if needed for components
            borderRadius: {
                xl: "1rem",   // Card radius
                lg: "0.5rem", // Button radius
            },
        },
    },
    plugins: [],
}
