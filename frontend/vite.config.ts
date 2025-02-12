/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import analog from '@analogjs/platform';
import { codecovVitePlugin } from '@codecov/vite-plugin';
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import viteTsConfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig(() => {
  return {
    root: __dirname,
    cacheDir: './node_modules/.vite',
    build: {
      outDir: './dist/capellacollab',
      reportCompressedSize: true,
      target: ['es2020'],
    },
    plugins: [
      analog({
        ssr: false,
        static: true,
        prerender: {
          routes: [],
        },
      }),
      viteStaticCopy({
        targets: [
          {
            src: 'node_modules/monaco-editor/**/*',
            dest: 'assets/monaco',
          },
        ],
      }),
      viteTsConfigPaths(),
      codecovVitePlugin({
        enableBundleAnalysis: process.env.CODECOV_TOKEN !== undefined,
        bundleName: 'capella-collab-manager',
        uploadToken: process.env.CODECOV_TOKEN,
        gitService: 'github',
        telemetry: false,
      }),
    ],
    server: {
      fs: {
        allow: ['.'],
      },
    },
  };
});
