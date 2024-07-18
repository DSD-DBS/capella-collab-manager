/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 *
 * Capella Collaboration
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * Do not edit the class manually.
 + To generate a new version, run `make openapi` in the root directory of this repository.
 */

import { ToolSessionConnectionInput } from './tool-session-connection-input';
import { PersistentWorkspaceSessionConfigurationInput } from './persistent-workspace-session-configuration-input';
import { Environment } from './environment';
import { ResourcesInput } from './resources-input';
import { SessionMonitoringInput } from './session-monitoring-input';
import { ToolModelProvisioningInput } from './tool-model-provisioning-input';


export interface ToolSessionConfigurationInput { 
    resources?: ResourcesInput;
    /**
     * Environment variables, which are mounted into session containers. You can use f-strings to reference other environment variables in the value. 
     */
    environment?: { [key: string]: Environment; };
    connection?: ToolSessionConnectionInput;
    monitoring?: SessionMonitoringInput;
    /**
     * Configuration regarding read-only sessions & automatic session provisioning.
     */
    provisioning?: ToolModelProvisioningInput;
    /**
     * Configuration for persistent workspaces.
     */
    persistent_workspaces?: PersistentWorkspaceSessionConfigurationInput;
}

