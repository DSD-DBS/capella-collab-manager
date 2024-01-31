/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    extend: {
      colors: {
        primary: "var(--primary-color)",
        error: "var(--error-color)",
        warning: "var(--warning-color)",
        success: "var(--success-color)",
        hover: "var(--hover-color)",
        archived: "#D1D5DB",
        url: "#2563eb",
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
    },
  },
  plugins: [],
};
