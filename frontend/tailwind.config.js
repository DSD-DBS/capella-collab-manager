/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
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
      },
      spacing: {
        button: "0.5rem",
        separator: "0.5rem",
        card: "400px",
        "m-card": "1rem",
      },
    },
  },
  plugins: [],
};
