/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

interface ImportMetaEnv {
  readonly VITE_BACKEND_URL: string;
  readonly VITE_API_DOCS_URL: string;
  readonly VITE_DOCS_URL: string;
  readonly VITE_PROMETHEUS_URL: string;
  readonly VITE_GRAFANA_URL: string;
  readonly VITE_SMTP_MOCK_URL: string;
  BASE_URL: string;
  MODE: string;
  DEV: boolean;
  PROD: boolean;
  SSR: boolean;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
