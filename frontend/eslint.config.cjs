/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
const eslint = require("@eslint/js");
const angular = require("angular-eslint");
const storybook = require("eslint-plugin-storybook");
const tailwind = require("eslint-plugin-tailwindcss");
const unusedImports = require("eslint-plugin-unused-imports");
const tseslint = require("typescript-eslint");

module.exports = tseslint.config(
  { ignores: ["dist", "tmp", "out-tsc", "**/*.spec.ts", "**/.storybook/**"] },
  {
    files: ["**/*.ts"],
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: __dirname,
      },
    },
    extends: [
      eslint.configs.recommended,
      ...tseslint.configs.recommended,
      ...tseslint.configs.stylistic,
      ...angular.configs.tsRecommended,
    ],
    processor: angular.processInlineTemplates,
    plugins: {
      "unused-imports": unusedImports,
    },
    rules: {
      "no-console": ["error", { allow: ["error"] }],
      "@angular-eslint/directive-selector": [
        "error",
        {
          type: "attribute",
          prefix: "app",
          style: "camelCase",
        },
      ],
      "@angular-eslint/use-lifecycle-interface": "error",
      "@typescript-eslint/no-deprecated": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
      "unused-imports/no-unused-imports": "error",
    },
  },
  {
    files: ["**/*.html"],
    extends: [
      ...angular.configs.templateRecommended,
      ...tailwind.configs["flat/recommended"],
    ],
    settings: {
      tailwindcss: {
        config: "frontend/tailwind.config.cjs",
        cssFiles: [
          "frontend/**/*.css",
          "frontend/**/*.scss",
          "!**/node_modules",
          "!**/.*",
          "!**/dist",
          "!**/build",
        ],
      },
    },
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
  {
    files: ["**/*.stories.ts"],
    extends: [...storybook.configs["flat/recommended"]],
  },
);
