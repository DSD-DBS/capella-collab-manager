import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GitModelService {
  constructor(private http: HttpClient) {}

  getGitRepositoriesForRepository(
    repository_name: string
  ): Observable<Array<GitModel>> {
    return this.http.get<Array<GitModel>>(
      environment.backend_url +
        '/repositories/' +
        repository_name +
        '/git-models/'
    );
  }

  unassignGitRepositoriesFromRepository(
    repository_name: string,
    model_id: number
  ): Observable<void> {
    return this.http.delete<void>(
      environment.backend_url +
        '/repositories/' +
        repository_name +
        '/git-models/' +
        model_id
    );
  }

  assignGitRepositoryToRepository(
    repository_name: string,
    body: CreateGitModel
  ): Observable<GitModel> {
    return this.http.post<GitModel>(
      environment.backend_url +
        '/repositories/' +
        repository_name +
        '/git-models/',
      body
    );
  }

  makeGitRepositoryPrimary(
    repository_name: string,
    model_id: number
  ): Observable<GitModel> {
    return this.http.patch<GitModel>(
      environment.backend_url +
        '/repositories/' +
        repository_name +
        '/git-models/' +
        model_id,
      { primary: true }
    );
  }
}

export interface GitModel extends CreateGitModel {
  id: number;
  primary: boolean;
}

export interface CreateGitModel {
  name: string;
  project_id: number;
  model: {
    path: string;
    entrypoint: string;
    revision: string;
  };
}
