import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class T4CRepoService {
  constructor(private http: HttpClient) {}
  repositories: Array<T4CRepository> = [];

  getRepositoryProjects(repository: string): Observable<Array<T4CRepository>> {
    return this.http
      .get<Array<T4CRepository>>(
        `${environment.backend_url}/repositories/${repository}/projects`
      )
      .pipe(
        tap((res: Array<T4CRepository>) => {
          this.repositories = res;
        })
      );
  }

  createRepositoryProject(
    repository: string,
    project_name: string
  ): Observable<T4CRepository> {
    return this.http.post<T4CRepository>(
      `${environment.backend_url}/repositories/${repository}/projects`,
      { name: project_name }
    );
  }

  deleteRepositoryProject(
    repository: string,
    project_id: number
  ): Observable<T4CRepository> {
    return this.http.delete<T4CRepository>(
      `${environment.backend_url}/repositories/${repository}/projects/${project_id}`
    );
  }
}

export interface T4CRepository {
  id: number;
  name: string;
  repository_name: string;
}
