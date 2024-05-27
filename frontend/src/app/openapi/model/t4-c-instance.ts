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

import { ToolVersion } from './tool-version';
import { Protocol } from './protocol';


export interface T4CInstance { 
    license: string;
    host: string;
    port: number;
    cdo_port: number;
    http_port: number | null;
    usage_api: string;
    rest_api: string;
    username: string;
    protocol: Protocol;
    name: string;
    version_id: number;
    id: number;
    version: ToolVersion;
    is_archived: boolean;
}
export namespace T4CInstance {
}

