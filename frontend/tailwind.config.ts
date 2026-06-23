import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        slatePanel: "#24313d",
        mist: "#f5f7f9",
        line: "#d8e0e7",
        teal: "#0f766e",
        cobalt: "#2454a6",
        amber: "#b7791f",
        risk: "#b42318"
      },
      boxShadow: {
        panel: "0 12px 28px rgba(23, 32, 42, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
