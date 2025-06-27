/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import type { StorybookConfig } from '@storybook/angular';

const config: StorybookConfig = {
  stories: ['../src/storybook/index.mdx', '../src/**/*.stories.ts'],
  addons: ['@storybook/addon-links', 'storycap', '@storybook/addon-docs'],
  framework: {
    name: '@storybook/angular',
    options: {},
  },
  staticDirs: [
    { from: './test-assets', to: '/test-assets' },
    { from: '../public', to: '/' },
  ],
  core: {
    disableTelemetry: true,
    enableCrashReports: false,
  },
};
export default config;
