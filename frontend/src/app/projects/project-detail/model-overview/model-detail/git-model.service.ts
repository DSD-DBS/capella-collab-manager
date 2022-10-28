/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GitModelService {
  BACKEND_URL_PREFIX = environment.backend_url;

  constructor(private http: HttpClient) {}

  private _gitModel = new Subject<GetGitModel>();
  private _gitModels = new BehaviorSubject<Array<GetGitModel>>([]);

  readonly gitModel = this._gitModel.asObservable();
  readonly gitModels = this._gitModels.asObservable();

  loadGitModels(project_slug: string, model_slug: string): void {
    this.http
      .get<Array<GetGitModel>>(
        this.BACKEND_URL_PREFIX +
          `/projects/${project_slug}/models/${model_slug}/git`
      )
      .subscribe((gitModels) => this._gitModels.next(gitModels));
  }

  loadGitModelById(
    project_slug: string,
    model_slug: string,
    git_model_id: number
  ): void {
    this.http
      .get<GetGitModel>(
        this.BACKEND_URL_PREFIX +
          `/projects/${project_slug}/models/${model_slug}/git/${git_model_id}`
      )
      .subscribe((gitModel) => this._gitModel.next(gitModel));
  }

  updateGitInstance(
    project_slug: string,
    model_slug: string,
    git_model_id: number,
    gitModel: PatchGitModel
  ): Observable<GetGitModel> {
    return this.http
      .patch<GetGitModel>(
        this.BACKEND_URL_PREFIX +
          `/projects/${project_slug}/models/${model_slug}/git/${git_model_id}`,
        gitModel
      )
      .pipe(
        tap((gitModel) => {
          this.loadGitModels(project_slug, model_slug);
          this._gitModel.next(gitModel);
        })
      );
  }

  makeGitInstancePrimary(
    project_slug: string,
    model_slug: string,
    git_model_id: number
  ): Observable<GetGitModel> {
    return this.http
      .patch<GetGitModel>(
        this.BACKEND_URL_PREFIX +
          `/projects/${project_slug}/models/${model_slug}/git/${git_model_id}`,
        true
      )
      .pipe(
        tap((gitModel) => {
          this.loadGitModels(project_slug, model_slug);
          this._gitModel.next(gitModel);
        })
      );
  }

  addGitSource(
    project_slug: string,
    model_slug: string,
    source: CreateGitModel
  ): Observable<GetGitModel> {
    return this.http.post<GetGitModel>(
      environment.backend_url +
        `/projects/${project_slug}/models/${model_slug}/modelsources/git`,
      source
    );
  }
}

export interface BaseGitModel {
  path: string;
  revision: string;
  entrypoint: string;
  username: string;
}

export interface CreateGitModel extends BaseGitModel {
  password?: string;
}

export interface PatchGitModel extends CreateGitModel {
  primary: boolean;
}

export interface GetGitModel extends BaseGitModel {
  id: number;
  primary: boolean;
  password: boolean;
}
