/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { BehaviorSubject } from 'rxjs';
import { ToolModel } from 'src/app/openapi';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { mockPrimaryGitModel } from './git';
import { mockTool, mockToolNature, mockToolVersion } from './tool';

export function createModelWithId(id: number): ToolModel {
  return {
    id: 1,
    name: `fakeModelName-${id}`,
    slug: `fakeModelSlug-${id}`,
    description: `fakeModelDescription-${id}`,
    tool: mockTool,
    version: mockToolVersion,
    t4c_models: [],
    git_models: [mockPrimaryGitModel],
    restrictions: { allow_pure_variants: false },
    display_order: 1,
    nature: mockToolNature,
  };
}

export const mockModel: Readonly<ToolModel> = createModelWithId(1);

export class MockModelWrapperService implements Partial<ModelWrapperService> {
  private _model = new BehaviorSubject<ToolModel | undefined>(undefined);
  private _models = new BehaviorSubject<ToolModel[] | undefined>(undefined);

  public readonly model$ = this._model.asObservable();
  public readonly models$ = this._models.asObservable();

  constructor(model: ToolModel, models: ToolModel[]) {
    this._model.next(model);
    this._models.next(models);
  }
}
