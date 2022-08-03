import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ProjectService } from 'src/app/projects/service/project.service';
import { environment } from 'src/environments/environment';
import { GitModel, ModelService } from '../model/model.service';

export interface Source {
  path: string,
  entrypoint: string,
  revision: string,
  username: string,
  password: string,
}

@Injectable({
  providedIn: 'root'
})
export class SourceService {

  constructor(
    private http: HttpClient,
    private projectService: ProjectService,
    private modelService: ModelService,
  ) { }

  source: Source | null = null;
  sources: Source[] | null = null;

  addGitSource(project_slug: string, model_slug: string, source: Source): Observable<Source> {
    return new Observable<Source>(subscriber => {
      this.projectService.init(project_slug).subscribe(project => {
        this.http.post<Source>(environment.backend_url + '/projects/'
          + project.name + '/extensions/modelsources/git/create/'
          + model_slug,
          source
        ).subscribe(new_source => {
          subscriber.next(new_source);
          subscriber.complete();
        })
      })
    })
  }
}
