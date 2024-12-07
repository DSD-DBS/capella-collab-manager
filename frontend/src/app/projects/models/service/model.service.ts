/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, forkJoin, map, Observable, take, tap } from 'rxjs';
import slugify from 'slugify';
import {
  GitModel,
  PatchToolModel,
  PostToolModel,
  ProjectsModelsService,
  SimpleToolModelWithoutProject,
  ToolModel,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class ModelWrapperService {
  constructor(private modelsService: ProjectsModelsService) {}

  private _model = new BehaviorSubject<ToolModel | undefined>(undefined);
  private _models = new BehaviorSubject<ToolModel[] | undefined>(undefined);

  public readonly model$ = this._model.asObservable();
  public readonly models$ = this._models.asObservable();

  loadModels(projectSlug: string): void {
    this.modelsService.getModels(projectSlug).subscribe({
      next: (models) => this._models.next(models),
      error: () => this._models.next(undefined),
    });
  }

  loadModelbySlug(modelSlug: string, projectSlug: string): void {
    this.modelsService.getModelBySlug(projectSlug, modelSlug).subscribe({
      next: (model) => this._model.next(model),
      error: () => this._model.next(undefined),
    });
  }

  createModel(
    projectSlug: string,
    model: PostToolModel,
  ): Observable<ToolModel> {
    return this.modelsService.createNewToolModel(projectSlug, model).pipe(
      tap({
        next: (model) => {
          this.loadModels(projectSlug);
          this._model.next(model);
        },
        error: () => this._model.next(undefined),
      }),
    );
  }

  setToolDetailsForModel(
    projectSlug: string,
    modelSlug: string,
    version_id: number,
    nature_id: number,
  ): Observable<ToolModel> {
    return this.modelsService
      .patchToolModel(projectSlug, modelSlug, {
        version_id,
        nature_id,
      })
      .pipe(
        tap({
          next: (model) => {
            this.loadModels(projectSlug);
            this._model.next(model);
          },
          error: () => this._model.next(undefined),
        }),
      );
  }

  private applyModelPatch(
    projectSlug: string,
    modelSlug: string,
    patchData: PatchToolModel,
  ): Observable<ToolModel> {
    return this.modelsService.patchToolModel(projectSlug, modelSlug, patchData);
  }

  updateModel(
    projectSlug: string,
    modelSlug: string,
    patchModel: PatchToolModel,
  ): Observable<ToolModel> {
    return this.applyModelPatch(projectSlug, modelSlug, patchModel).pipe(
      tap({
        next: (model) => {
          this.loadModels(projectSlug);
          this._model.next(model);
        },
      }),
    );
  }

  updateModels(
    projectSlug: string,
    modelUpdates: { modelSlug: string; patchModel: PatchToolModel }[],
  ): Observable<ToolModel[]> {
    const updateObservables = modelUpdates.map(({ modelSlug, patchModel }) =>
      this.applyModelPatch(projectSlug, modelSlug, patchModel),
    );

    return forkJoin(updateObservables).pipe(
      tap({
        next: (models: ToolModel[]) => {
          this.loadModels(projectSlug);
          this._model.next(models[models.length - 1]);
        },
      }),
    );
  }

  deleteModel(projectSlug: string, modelSlug: string): Observable<void> {
    return this.modelsService.deleteToolModel(projectSlug, modelSlug).pipe(
      tap(() => {
        this.loadModels(projectSlug);
        this._model.next(undefined);
      }),
    );
  }

  clearModel(): void {
    this._model.next(undefined);
  }

  clearModels(): void {
    this._models.next(undefined);
  }

  asyncSlugValidator(ignoreModel?: ToolModel): AsyncValidatorFn {
    const ignoreSlug = ignoreModel ? ignoreModel.slug : -1;
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      const modelSlug = slugify(control.value, { lower: true });
      return this.models$.pipe(
        take(1),
        map((models) => {
          return models?.find(
            (model) => model.slug === modelSlug && model.slug !== ignoreSlug,
          )
            ? { uniqueSlug: { value: modelSlug } }
            : null;
        }),
      );
    };
  }
}

export function getPrimaryGitModel(
  model: SimpleToolModelWithoutProject,
): GitModel | undefined {
  return model.git_models?.find((gitModel) => gitModel.primary);
}
