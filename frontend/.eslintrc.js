/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
        // Reenable when the following bug is fixed:
        // https://github.com/sweepline/eslint-plugin-unused-imports/issues/77
        // "unused-imports/no-unused-imports": "error",
        "no-console": ["error", { allow: ["error"] }],
        "deprecation/deprecation": "error",
        "@angular-eslint/use-lifecycle-interface": "error",
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
        "tailwindcss/no-custom-classname": [
          "error",
          {
            whitelist: ["language-python"],
          },
        ],
        "tailwindcss/enforces-negative-arbitrary-values": "error",
        "tailwindcss/enforces-shorthand": "error",
        "tailwindcss/no-contradicting-classname": "error",
      },
    },
  ],
  extends: ["plugin:storybook/recommended"],
};
