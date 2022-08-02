import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { GitModel, ModelService } from '../model/model.service';

export interface Source {
  model_id: number,
  name: string,
  path: string,
  entrypoint: string,
  revision: string,
  primary: boolean,
  username: string,
  password: string,
}

@Injectable({
  providedIn: 'root'
})
export class SourceService {

  constructor(
    private http: HttpClient,
    private modelService: ModelService,
  ) { }

  source: Source | null = null;
  sources: Source[] | null = null;

  addGitSource(project_slug: string, model_slug: string, source: GitModel) {
    this.http.post();
  }
}
