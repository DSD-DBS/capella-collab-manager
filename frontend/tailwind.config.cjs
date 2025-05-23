/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
const defaultTheme = require("tailwindcss/defaultTheme");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Roboto", ...defaultTheme.fontFamily.sans],
        special: [
          "Comic Sans MS",
          "Chalkboard",
          ...defaultTheme.fontFamily.sans,
        ],
      },
      colors: {
        primary: "var(--primary-color)",
        error: "var(--error-color)",
        warning: "var(--warning-color)",
        success: "var(--success-color)",
        banner: "var(--banner-color)",
        hover: "var(--hover-color)",
        archived: "#D1D5DB",
        url: "#2563eb",
        warn: "#f44336",
      },
      spacing: {
        button: "0.5rem",
        separator: "0.5rem",
        card: "400px",
        "wide-card": "600px",
        "m-card": "1rem",
        // The mat-cards should not overflow the screen
        // 2*3.9px is the margin of the wrapper
        // 2*10px is the margin of the mat-card
        "max-card": "calc(100vw - 2*3.9px - 2*10px)",
      },
      borderRadius: {
        material: "28px",
      },
      screens: {
        tall: { raw: "(min-height: 945px)" },
      },
      backgroundImage: {
        hazard:
          "repeating-linear-gradient(-55deg, #000, #000 10px, #966708 10px, #966708 20px)",
      },
    },
  },
  plugins: [],
};
