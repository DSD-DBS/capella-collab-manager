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

import { BaseUser } from './base-user';
import { SessionType } from './session-type';
import { Message } from './message';
import { ToolVersionWithTool } from './tool-version-with-tool';
import { ToolSessionConnectionMethod } from './tool-session-connection-method';
import { SessionSharing } from './session-sharing';


export interface Session { 
    id: string;
    type: SessionType;
    created_at: string;
    owner: BaseUser;
    version: ToolVersionWithTool;
    state: string;
    warnings: Array<Message>;
    last_seen: string;
    connection_method_id: string;
    connection_method: ToolSessionConnectionMethod | null;
    shared_with: Array<SessionSharing>;
}
export namespace Session {
}


