/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: CC0-1.0
 */

module.exports = {
  settings: {
    tailwindcss: {
      config: "frontend/tailwind.config.js",
      cssFiles: [
        "frontend/**/*.css",
        "!**/node_modules",
        "!**/.*",
        "!**/dist",
        "!**/build",
      ],
    },
  },
  overrides: [
    {
      files: ["*.ts"],
      parserOptions: {
        project: ["tsconfig.json"],
        tsconfigRootDir: __dirname,
        createDefaultProgram: true,
      },
      extends: [
        "plugin:@typescript-eslint/recommended",
        "plugin:@angular-eslint/recommended",
        "plugin:@angular-eslint/template/process-inline-templates",
      ],
      plugins: ["import", "unused-imports", "deprecation"],
      rules: {
        "@angular-eslint/directive-selector": [
          "error",
          {
            type: "attribute",
            prefix: "app",
            style: "camelCase",
          },
        ],
        "import/order": [
          "error",
          {
            alphabetize: {
              order: "asc",
            },
          },
        ],
        "@angular-eslint/sort-ngmodule-metadata-arrays": ["error"],
        "@typescript-eslint/no-unused-vars": [
          "error",
          {
            argsIgnorePattern: "^_",
            varsIgnorePattern: "^_",
            caughtErrorsIgnorePattern: "^_",
          },
        ],
        "unused-imports/no-unused-imports": "error",
        "no-console": ["error", { allow: ["error"] }],
        "deprecation/deprecation": "warn",
      },
    },
    {
      files: ["*.html"],
      extends: [
        "plugin:@angular-eslint/template/recommended",
        "plugin:tailwindcss/recommended",
      ],
      parser: "@angular-eslint/template-parser",
      rules: {
        "tailwindcss/classnames-order": "off",
        "tailwindcss/no-custom-classname": "error",
        "tailwindcss/enforces-negative-arbitrary-values": "error",
        "tailwindcss/enforces-shorthand": "error",
        "tailwindcss/no-contradicting-classname": "error",
      },
    },
  ],
};
