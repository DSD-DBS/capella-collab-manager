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


export interface CustomNavbarLink { 
    name: string;
    /**
     * Role required to see this link.
     */
    role: Role;
    /**
     * URL to link to.
     */
    href: string;
}
export namespace CustomNavbarLink {
}


