/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 *
 * Capella Collaboration Manager API
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * Do not edit the class manually.
 + To generate a new version, run `make openapi` in the root directory of this repository.
 */



/**
 * Side-car container to push logs to Grafana Loki
 */
export interface LoggingConfigurationOutput { 
    /**
     * If enabled, logs will be pushed to Grafana Loki.
     */
    enabled: boolean;
    /**
     * Path to the log files, can be a glob string.
     */
    path: string;
}

