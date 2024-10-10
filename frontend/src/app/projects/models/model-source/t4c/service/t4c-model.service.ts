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
import {
  BehaviorSubject,
  Observable,
  combineLatest,
  map,
  take,
  tap,
} from 'rxjs';
import {
  ProjectsModelsT4CService,
  SimpleT4CModelWithRepository,
  SubmitT4CModel,
} from 'src/app/openapi';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';

@Injectable({
  providedIn: 'root',
})
export class T4CModelService {
  constructor(
    private modelWrapperService: ModelWrapperService,
    private t4cInstanceWrapperService: T4CInstanceWrapperService,
    private t4cModelService: ProjectsModelsT4CService,
  ) {}

  private _t4cModel = new BehaviorSubject<
    SimpleT4CModelWithRepository | undefined
  >(undefined);
  public readonly t4cModel$ = this._t4cModel.asObservable();

  private _t4cModels = new BehaviorSubject<
    SimpleT4CModelWithRepository[] | undefined
  >(undefined);
  public readonly t4cModels$ = this._t4cModels.asObservable();

  compatibleT4CInstances$ = combineLatest([
    this.modelWrapperService.model$,
    this.t4cInstanceWrapperService.t4cInstances$,
  ]).pipe(
    map(([model, instances]) => {
      return instances?.filter(
        (instance) =>
          model?.version?.config.compatible_versions.includes(
            instance.version.id,
          ) || model?.version?.id === instance.version.id,
      );
    }),
  );

  loadT4CModels(projectSlug: string, modelSlug: string): void {
    this.t4cModelService.listT4cModels(projectSlug, modelSlug).subscribe({
      next: (models) => this._t4cModels.next(models),
      error: () => this._t4cModels.next(undefined),
    });
  }

  loadT4CModel(projectSlug: string, modelSlug: string, id: number): void {
    this.t4cModelService.getT4cModel(projectSlug, id, modelSlug).subscribe({
      next: (model) => this._t4cModel.next(model),
      error: () => this._t4cModel.next(undefined),
    });
  }

  createT4CModel(
    projectSlug: string,
    modelSlug: string,
    body: SubmitT4CModel,
  ): Observable<SimpleT4CModelWithRepository> {
    return this.t4cModelService
      .createT4cModel(projectSlug, modelSlug, body)
      .pipe(
        tap((model) => {
          this._t4cModel.next(model);
          this.loadT4CModels(projectSlug, modelSlug);
        }),
      );
  }

  patchT4CModel(
    projectSlug: string,
    modelSlug: string,
    t4cModelID: number,
    body: SubmitT4CModel,
  ): Observable<SimpleT4CModelWithRepository> {
    return this.t4cModelService
      .updateT4cModel(projectSlug, t4cModelID, modelSlug, body)
      .pipe(
        tap((model) => {
          this._t4cModel.next(model);
          this.loadT4CModels(projectSlug, modelSlug);
        }),
      );
  }

  unlinkT4CModel(
    projectSlug: string,
    modelSlug: string,
    t4cModelId: number,
  ): Observable<void> {
    return this.t4cModelService
      .deleteT4cModel(projectSlug, t4cModelId, modelSlug)
      .pipe(
        tap(() => {
          this._t4cModel.next(undefined);
          this.loadT4CModels(projectSlug, modelSlug);
        }),
      );
  }

  reset() {
    this._t4cModels.next(undefined);
    this._t4cModel.next(undefined);
  }

  asyncNameValidator(
    instanceId: number,
    repositoryId: number,
  ): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.t4cModels$.pipe(
        take(1),
        map((t4cModels) => {
          const nameExists = t4cModels?.find(
            (model) =>
              model.repository.id === repositoryId &&
              model.repository.instance.id === instanceId &&
              model.name === control.value,
          );
          return nameExists ? { uniqueName: { value: control.value } } : null;
        }),
      );
    };
  }
}
