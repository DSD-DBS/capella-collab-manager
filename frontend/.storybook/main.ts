/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import type { StorybookConfig } from '@storybook/angular';

const config: StorybookConfig = {
  stories: [
    '../src/storybook/index.mdx',
    '../src/**/*.mdx',
    '../src/**/*.stories.ts',
  ],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    'storycap',
  ],
  framework: {
    name: '@storybook/angular',
    options: {},
  },
  core: {
    disableTelemetry: true,
    enableCrashReports: false,
    builder: {
      name: '@storybook/builder-webpack5',
      options: {
        lazyCompilation: false, // lazyCompilation breaks Storycap
      },
    },
  },
};
export default config;
