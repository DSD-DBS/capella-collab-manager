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
  // Exclude monaco-editor from existing Angular CSS loader
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
      use: [
        'style-loader',
        {
          loader: 'css-loader',
          options: {
            // https://github.com/webpack/webpack-dev-server/issues/1815#issuecomment-1181720815
            url: false,
          },
        },
      ],
    },
    {
      test: /\.ttf$/,
      include: /node_modules\/monaco-editor/,
      type: 'asset/resource',
    },
  );
  return config;
};
