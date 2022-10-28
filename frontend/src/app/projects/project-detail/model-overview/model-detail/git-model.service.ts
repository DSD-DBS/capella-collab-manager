/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject, tap } from 'rxjs';
import {
  GitModel,
  PatchGitModel,
} from 'src/app/services/source/source.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GitModelService {
  BACKEND_URL_PREFIX = environment.backend_url;

  constructor(private http: HttpClient) {}

  private _gitModel = new Subject<GitModel>();
  private _gitModels = new BehaviorSubject<Array<GitModel>>([]);

  readonly gitModel = this._gitModel.asObservable();
  readonly gitModels = this._gitModels.asObservable();

  loadGitModels(project_slug: string, model_slug: string): void {
    this.http
      .get<Array<GitModel>>(
        this.BACKEND_URL_PREFIX +
          `/projects/${project_slug}/models/${model_slug}/git/git-models`
      )
      .subscribe((gitModels) => this._gitModels.next(gitModels));
  }

  loadGitModelById(
    project_slug: string,
    model_slug: string,
    git_model_id: number
  ): void {
    this.http
      .get<GitModel>(
        this.BACKEND_URL_PREFIX +
          `/projects/${project_slug}/models/${model_slug}/git/git-model/${git_model_id}`
      )
      .subscribe((gitModel) => this._gitModel.next(gitModel));
  }

  updateGitInstance(
    project_slug: string,
    model_slug: string,
    git_model_id: number,
    gitModel: PatchGitModel
  ): Observable<GitModel> {
    return this.http
      .patch<GitModel>(
        this.BACKEND_URL_PREFIX +
          `/projects/${project_slug}/models/${model_slug}/git/git-model/${git_model_id}`,
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
  ): Observable<GitModel> {
    return this.http
      .patch<GitModel>(
        this.BACKEND_URL_PREFIX +
          `/projects/${project_slug}/models/${model_slug}/git/git-model/${git_model_id}`,
        true
      )
      .pipe(
        tap((gitModel) => {
          this.loadGitModels(project_slug, model_slug);
          this._gitModel.next(gitModel);
        })
      );
  }
}
