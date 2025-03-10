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



export interface ToolIntegrationsOutput { 
    /**
     * Enables support for TeamForCapella. If enabled, TeamForCapella repositories will be shown as model sources for corresponding models. Also, session tokens are created for corresponding sessions. Please refer to the documentation for more details. 
     */
    t4c: boolean;
    /**
     * Enables support for pure::variants. If enabled and the restrictions are met, pure::variants license secrets & information will be mounted to containers. Please refer to the documentation for more details. 
     */
    pure_variants: boolean;
}

