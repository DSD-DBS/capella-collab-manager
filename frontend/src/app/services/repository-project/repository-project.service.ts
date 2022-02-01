import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class RepositoryProjectService {
  constructor(private http: HttpClient) {}

  getRepositoryProjects(
    repository: string
  ): Observable<Array<RepositoryProject>> {
    return this.http.get<Array<RepositoryProject>>(
      `${environment.backend_url}/repositories/${repository}/projects`
    );
  }

  createRepositoryProject(
    repository: string,
    project_name: string
  ): Observable<RepositoryProject> {
    return this.http.post<RepositoryProject>(
      `${environment.backend_url}/repositories/${repository}/projects`,
      { name: project_name }
    );
  }

  deleteRepositoryProject(
    repository: string,
    project_id: number
  ): Observable<RepositoryProject> {
    return this.http.delete<RepositoryProject>(
      `${environment.backend_url}/repositories/${repository}/projects/${project_id}`
    );
  }
}

export interface RepositoryProject {
  id: number;
  name: string;
  repository_name: string;
}
