/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

export const environment = {
  production: false,
  backend_url: 'http://localhost:4200/api/v1',
  privacy: 'https://example.com/privacy',
  imprint: 'https://example.com/imprint',
  provider: 'PROVIDER',
  authentication: 'OAuth mock',
  usernameAttribute: 'sub',
  integrations: {
    modelsources: {
      t4c: true,
      git: true,
    },
  },
};
