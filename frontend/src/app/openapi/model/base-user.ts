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

import { Role } from './role';


export interface BaseUser { 
    id: number;
    name: string;
    idp_identifier: string;
    email: string | null;
    role: Role;
    beta_tester: boolean;
    blocked: boolean;
}
export namespace BaseUser {
}


