/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import MonacoWebpackPlugin from 'monaco-editor-webpack-plugin';
import * as webpack from 'webpack';

export default (config: webpack.Configuration) => {
  config?.plugins?.push(
    new MonacoWebpackPlugin({
      languages: ['yaml'],
    }),
  );
  // Exclude monaco-editor existing css loader
  const cssRuleIdx = config?.module?.rules?.findIndex(
    (rule: false | '' | 0 | webpack.RuleSetRule | '...' | null | undefined) =>
      (rule as webpack.RuleSetRule).test?.toString().includes(':css'),
  );
  if (cssRuleIdx !== -1 && cssRuleIdx !== undefined) {
    const rule = config?.module?.rules![cssRuleIdx];
    (rule as webpack.RuleSetRule).exclude = /node_modules\/monaco-editor/;
  }
  config?.module?.rules?.push(
    {
      test: /\.css$/,
      include: /node_modules\/monaco-editor/,
      use: ['style-loader', 'css-loader'],
    },
    {
      test: /\.ttf$/,
      use: ['file-loader'],
    },
  );
  return config;
};
