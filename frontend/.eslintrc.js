/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: CC0-1.0
 */

module.exports = {
  overrides: [
    {
      files: ["*.ts"],
      parserOptions: {
        project: ["tsconfig.json"],
        tsconfigRootDir: __dirname,
        createDefaultProgram: true,
      },
      extends: [
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
        /* Find a proper naming strategy
        "@angular-eslint/component-selector": [
          "error",
          {
            type: "element",
            prefix: "app",
            style: "kebab-case",
          },
        ], */
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
        "@typescript-eslint/no-restricted-imports": [
          "error",
          {
            name: "no-relative-imports",
            patterns: ["../../../*"],
            message: "Please use absolute imports instead",
          },
        ],
        "unused-imports/no-unused-imports": "error",
        "no-console": ["error", { allow: ["error"] }],
        "deprecation/deprecation": "error",
      },
    },
    {
      files: ["*.html"],
      extends: ["plugin:@angular-eslint/template/recommended"],
      rules: {},
    },
  ],
};
