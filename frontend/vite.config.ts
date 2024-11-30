/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import analog from '@analogjs/platform';
import { defineConfig } from 'vite';
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
      viteTsConfigPaths(),
    ],
    server: {
      fs: {
        allow: ['.'],
      },
    },
  };
});
