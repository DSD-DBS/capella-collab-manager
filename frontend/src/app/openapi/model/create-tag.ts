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

import { TagScope } from './tag-scope';


export interface CreateTag { 
    name: string;
    description?: string | null;
    icon?: string | null;
    hex_color: string;
    scope?: TagScope;
}
export namespace CreateTag {
}


