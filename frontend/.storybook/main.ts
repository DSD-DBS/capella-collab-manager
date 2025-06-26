/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

const config = {
  stories: ['../src/**/*.stories.ts'],
  framework: {
    name: '@storybook/angular',
    options: {
      builder: {
        name: '@storybook/builder-vite',
        options: {},
      },
    },
  },
  addons: ['@storybook/addon-links'],
  staticDirs: [{ from: './test-assets', to: '/test-assets' }],
  core: {
    disableTelemetry: true,
    enableCrashReports: false,
  },
  async viteFinal(config) {
    const { mergeConfig } = await import('vite');
    return mergeConfig(config, {
      // Override vite config here if needed
    });
  },
};

export default config;
