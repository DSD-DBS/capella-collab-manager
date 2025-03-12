/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import angular from '@analogjs/vite-plugin-angular';
import { codecovVitePlugin } from '@codecov/vite-plugin';
import gzipPlugin from 'rollup-plugin-gzip';
import { promisify } from 'util';
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import viteTsConfigPaths from 'vite-tsconfig-paths';
import { brotliCompress } from 'zlib';

const brotliPromise = promisify(brotliCompress);

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
      angular(),
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
      gzipPlugin({
        customCompression: (content) =>
          brotliPromise(
            Buffer.isBuffer(content) ? content : Buffer.from(content),
          ),
        fileName: '.br',
      }),
      gzipPlugin(),
    ],
    server: {
      fs: {
        allow: ['.'],
      },
    },
  };
});
