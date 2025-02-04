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

import { ToolSessionEnvironmentStage } from './tool-session-environment-stage';
import { ToolSessionEnvironmentOutput } from './tool-session-environment-output';


export interface EnvironmentValue1 { 
    /**
     * Stage of the environment variable injection. \'before\' runs before the environment variable is stringified, allowing extended filtering and manipulation. For example, you can access the path of the first provisioned model with \'{CAPELLACOLLAB_SESSION_PROVISIONING[0][path]}\'. If you provide a dict, it will use Pythons default dict serialization and will not JSON serialization! \'after\' runs after the environment variable is JSON serialized, allowing to access a dict in the JSON format. 
     */
    stage: ToolSessionEnvironmentStage;
    /**
     * Environment variables, which are mounted into session containers. You can use f-strings to reference other environment variables in the value. 
     */
    value: string;
}
export namespace EnvironmentValue1 {
}


