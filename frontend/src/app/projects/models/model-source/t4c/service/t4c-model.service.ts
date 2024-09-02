/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, Observable, map, take, tap } from 'rxjs';
import { T4CRepository } from 'src/app/openapi';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class T4CModelService {
  constructor(private http: HttpClient) {}

  private _t4cModel = new BehaviorSubject<T4CModel | undefined>(undefined);
  public readonly t4cModel$ = this._t4cModel.asObservable();

  private _t4cModels = new BehaviorSubject<T4CModel[] | undefined>(undefined);
  public readonly t4cModels$ = this._t4cModels.asObservable();

  urlFactory(projectSlug: string, modelSlug: string): string {
    return `${environment.backend_url}/projects/${projectSlug}/models/${modelSlug}/modelsources/t4c`;
  }

  loadT4CModels(projectSlug: string, modelSlug: string): void {
    this.http
      .get<T4CModel[]>(this.urlFactory(projectSlug, modelSlug))
      .subscribe({
        next: (models) => this._t4cModels.next(models),
        error: () => this._t4cModels.next(undefined),
      });
  }

  loadT4CModel(projectSlug: string, modelSlug: string, id: number): void {
    this.http
      .get<T4CModel>(`${this.urlFactory(projectSlug, modelSlug)}/${id}`)
      .subscribe({
        next: (model) => this._t4cModel.next(model),
        error: () => this._t4cModel.next(undefined),
      });
  }

  createT4CModel(
    projectSlug: string,
    modelSlug: string,
    body: SubmitT4CModel,
  ): Observable<T4CModel> {
    return this.http
      .post<T4CModel>(this.urlFactory(projectSlug, modelSlug), body)
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
    t4c_model_id: number,
    body: SubmitT4CModel,
  ): Observable<T4CModel> {
    return this.http
      .patch<T4CModel>(
        `${this.urlFactory(projectSlug, modelSlug)}/${t4c_model_id}`,
        body,
      )
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
    return this.http
      .delete<void>(`${this.urlFactory(projectSlug, modelSlug)}/${t4cModelId}`)
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

export type SubmitT4CModel = {
  t4c_instance_id: number;
  t4c_repository_id: number;
  name: string;
};

export type T4CModel = {
  name: string;
  id: number;
  repository: T4CRepository;
};

export type SimpleT4CModel = {
  project_name: string;
  repository_name: string;
  instance_name: string;
};
