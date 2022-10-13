/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { GetGitModel } from 'src/app/services/source/source.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GitModelService {
  BACKEND_URL_PREFIX = environment.backend_url;
  base_url = new URL(environment.backend_url);

  constructor(private http: HttpClient) {}

  private _gitModels = new BehaviorSubject<Array<GetGitModel>>([]);

  readonly gitModels = this._gitModels.asObservable();

  loadGitSources(project_name: string, model_slug: string): void {
    this.http
      .get<Array<GetGitModel>>(
        this.base_url.toString() +
          `/projects/${project_name}/models/${model_slug}/git/git-models`
      )
      .subscribe((gitModels) => this._gitModels.next(gitModels));
  }
}
