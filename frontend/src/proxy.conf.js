/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */


PROXY_CONFIG = [
  {
    context: [
      "/api",
      "/default"
    ],
    "target": "http://localhost:8080",
    "secure": false,
    "logLevel": "debug"
  }
]

module.exports = PROXY_CONFIG
