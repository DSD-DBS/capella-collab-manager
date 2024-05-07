/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Model } from 'src/app/projects/models/service/model.service';
import { mockPrimaryGitModel } from './git';
import { mockTool, mockToolVersion } from './tool';

export function createModelWithId(id: number): Model {
  return {
    id: 1,
    name: `fakeModelName-${id}`,
    slug: `fakeModelSlug-${id}`,
    project_slug: 'fakeProjectSlug',
    description: `fakeModelDescription-${id}`,
    tool: mockTool,
    version: mockToolVersion,
    t4c_models: [],
    git_models: [mockPrimaryGitModel],
    restrictions: { allow_pure_variants: false },
    display_order: 1,
  };
}

export const mockModel: Readonly<Model> = createModelWithId(1);
