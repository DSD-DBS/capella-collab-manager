/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, Observable, of } from 'rxjs';
import {
  SimpleToolModel,
  SimpleToolModelWithoutProject,
  ToolModel,
} from 'src/app/openapi';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { mockProject } from 'src/storybook/project';
import { mockPrimaryGitModel } from './git';
import {
  mockCapellaTool,
  mockCapellaToolVersion,
  mockToolNature,
} from './tool';

export function createModelWithId(id: number): ToolModel {
  return {
    id: 1,
    name: `Model ${id}`,
    slug: `slug-${id}`,
    description: `This is the description of the model with id ${id}`,
    tool: mockCapellaTool,
    version: mockCapellaToolVersion,
    t4c_models: [],
    git_models: [mockPrimaryGitModel],
    restrictions: { allow_pure_variants: false },
    display_order: 1,
    nature: mockToolNature,
  };
}

export const mockModel: Readonly<ToolModel> = createModelWithId(1);
export const mockSimpleToolModel: Readonly<SimpleToolModel> = {
  ...mockModel,
  project: mockProject,
};
export const mockSimpleToolModelWithoutProject: Readonly<SimpleToolModelWithoutProject> =
  {
    id: 1,
    slug: 'in-flight-entertainment-system',
    name: 'In-Flight Entertainment System',
    git_models: [mockPrimaryGitModel],
  };

class MockModelWrapperService implements Partial<ModelWrapperService> {
  private _model = new BehaviorSubject<ToolModel | undefined>(undefined);
  private _models = new BehaviorSubject<ToolModel[] | undefined>(undefined);

  public readonly model$ = this._model.asObservable();
  public readonly models$ = this._models.asObservable();

  constructor(
    model: ToolModel | undefined = undefined,
    models: ToolModel[] | undefined = undefined,
  ) {
    this._model.next(model);
    this._models.next(models);
  }

  asyncSlugValidator(_ignoreModel?: ToolModel): AsyncValidatorFn {
    return (_control: AbstractControl): Observable<ValidationErrors | null> => {
      return of(null);
    };
  }
}

export const mockModelWrapperServiceProvider = (
  model: ToolModel | undefined = undefined,
  models: ToolModel[] | undefined = undefined,
) => {
  return {
    provide: ModelWrapperService,
    useValue: new MockModelWrapperService(model, models),
  };
};
