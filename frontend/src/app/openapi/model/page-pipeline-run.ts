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

import { PipelineRun } from './pipeline-run';


export interface PagePipelineRun { 
    items: Array<PipelineRun>;
    total?: number | null;
    page: number | null;
    size: number | null;
    pages?: number | null;
}

