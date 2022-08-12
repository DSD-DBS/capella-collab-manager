// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GitModelService {
  constructor(private http: HttpClient) {}
  models: Array<GitModel> = [];

  getGitRepositoriesForRepository(
    repository_name: string
  ): Observable<Array<GitModel>> {
    return this.http
      .get<Array<GitModel>>(
        environment.backend_url +
          '/projects/' +
          repository_name +
          '/extensions/modelsources/git'
      )
      .pipe(
        tap((res: Array<GitModel>) => {
          this.models = res;
        })
      );
  }

  unassignGitRepositoriesFromRepository(
    repository_name: string,
    model_id: number
  ): Observable<void> {
    return this.http.delete<void>(
      environment.backend_url +
        '/projects/' +
        repository_name +
        '/extensions/modelsources/git/' +
        model_id
    );
  }

  assignGitRepositoryToRepository(
    repository_name: string,
    body: CreateGitModel
  ): Observable<GitModel> {
    const reqBody = JSON.parse(JSON.stringify(body));
    // Base64 encoding is needed because some application gateways block urls in the requests
    reqBody.model.path = btoa(reqBody.model.path);
    return this.http.post<GitModel>(
      environment.backend_url +
        '/projects/' +
        repository_name +
        '/extensions/modelsources/git',
      reqBody
    );
  }

  makeGitRepositoryPrimary(
    repository_name: string,
    model_id: number
  ): Observable<GitModel> {
    return this.http.patch<GitModel>(
      environment.backend_url +
        '/projects/' +
        repository_name +
        '/extensions/modelsources/git/' +
        model_id,
      { primary: true }
    );
  }

  getRevisions(project_name: string) {
    return this.http.get<Revisions>(
      environment.backend_url +
        '/projects/' +
        project_name +
        '/extensions/modelsources/git/primary/revisions'
    );
  }
}

export interface GitModel extends BasicGitModel {
  id: number;
  primary: boolean;
  username: string;
}

export interface BasicGitModel {
  name: string;
  model: {
    path: string;
    entrypoint: string;
    revision: string;
  };
}

export interface CreateGitModel extends BasicGitModel {
  credentials: {
    username: string;
    password: string;
  };
}

export interface Revisions {
  branches: Array<string>;
  tags: Array<string>;
  default: string;
}
