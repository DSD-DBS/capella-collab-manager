/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

const config = {
  stories: ['../src/**/*.stories.ts'],
  framework: {
    name: '@analogjs/storybook-angular',
    options: {},
  },
  staticDirs: [{ from: './test-assets', to: '/test-assets' }],
  core: {
    disableTelemetry: true,
    enableCrashReports: false,
  },
};

export default config;
