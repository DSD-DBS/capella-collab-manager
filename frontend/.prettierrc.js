/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: CC0-1.0
 */

module.exports = {
  plugins: [
    require.resolve("prettier-plugin-tailwindcss"),
    require.resolve("@trivago/prettier-plugin-sort-imports"),
  ],
  importOrder: ["^[./]"],
  importOrderParserPlugins: ["typescript", "decorators-legacy"],
};
