/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

export const BACKEND_URL = import.meta.env
  ? import.meta.env.VITE_BACKEND_URL
  : 'about:blank';

export const API_DOCS_URL = import.meta.env
  ? import.meta.env.VITE_API_DOCS_URL
  : 'about:blank';

export const DOCS_URL = import.meta.env
  ? import.meta.env.VITE_DOCS_URL
  : 'about:blank';

export const PROMETHEUS_URL = import.meta.env
  ? import.meta.env.VITE_PROMETHEUS_URL
  : 'about:blank';

export const GRAFANA_URL = import.meta.env
  ? import.meta.env.VITE_GRAFANA_URL
  : 'about:blank';

export const SMTP_MOCK_URL = import.meta.env
  ? import.meta.env.VITE_SMTP_MOCK_URL
  : 'about:blank';
