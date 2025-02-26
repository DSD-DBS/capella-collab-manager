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



export interface ToolModelProvisioningInput { 
    /**
     * Directory, where models are provisioned. The directory is mounted into the session container.
     */
    directory?: string;
    max_number_of_models?: number | null;
    /**
     * Specifies if a tool requires provisioning. If enabled and a session without provisioning is requested, it will be declined.
     */
    required?: boolean;
    /**
     * If enabled, the diagram_cache attribute will be added to the provisioning dictionary.
     */
    provide_diagram_cache?: boolean;
}

