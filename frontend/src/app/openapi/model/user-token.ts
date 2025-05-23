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

import { BaseUser } from './base-user';
import { FineGrainedResourceOutput } from './fine-grained-resource-output';


export interface UserToken { 
    id: number;
    user: BaseUser;
    expiration_date: string;
    /**
     * The scope the token was requested for.
     */
    requested_scopes: FineGrainedResourceOutput;
    /**
     * The actual scope of the token. It might be less than the requested scope.
     */
    actual_scopes: FineGrainedResourceOutput;
    created_at: string | null;
    title: string;
    description: string;
    source: string;
    managed: boolean;
}

