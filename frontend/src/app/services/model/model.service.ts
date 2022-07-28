import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable, of, subscribeOn } from "rxjs";
import { ProjectService } from "src/app/projects/service/project.service";
import { environment } from "src/environments/environment";

export interface NewModel {
  name: string;
  description: string;
}

export interface EmptyModel extends NewModel {
  tool_id: number;
  version_id: string;
  type_id: string;
}

export interface GitModel extends NewModel {
  url: string;
  username: string;
  password: string;
  revision: string; 
  path: string; 
  entrypoint: string;
}

export interface OfflineModel extends NewModel {}

export interface Model {
  id: number;
  project_slug: string;
  slug: string;
  name: string;
  description: string;
  tool_id: number | null;
  version_id: number | null;
  type_id: number | null;
  t4c_model: number | null;
  git_model: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class ModelService {

  base_url = new URL('models/', environment.backend_url + '/')

  constructor(
    private http: HttpClient,
    private projectService: ProjectService,
  ) {}

  model: Model | null = null;
  models: Model[] | null = null;

  init(project_slug: string, model_slug: string): Observable<Model> {
    return new Observable<Model>(subscriber => {
      this.projectService.init(project_slug).subscribe(project => {
        if (this.model
          && (this.model.project_slug !== project_slug)
          && (this.model.slug === model_slug)
        ) {
          subscriber.next(this.model)
          subscriber.complete()
        } else {
          this.getSlug(model_slug, project.slug).subscribe(model => {
            subscriber.next(model)
            subscriber.complete()
          })
        }
      })
    })
  }

  init_all(project_slug: string): Observable<Model[]> {
    return new Observable<Model[]>(subscriber => {
      this.projectService.init(project_slug).subscribe(project => {
        if (this.models
          && (this.models[0].project_slug !== project_slug)
        ) {
          subscriber.next(this.models);
          subscriber.complete();
        } else {
          this.list(project.slug).subscribe(models => {
            subscriber.next(models);
            subscriber.complete();
          })
        }
      })
    })
  }

  list(project_slug: string, q: string | undefined = undefined): Observable<Model[]> {
    let url = new URL(project_slug, this.base_url);
    return new Observable<Model[]>(subscriber => {
      let result = q
      ? this.http.get<Model[]>(url.toString(), {params: {q}})
      : this.http.get<Model[]>(url.toString());
      result.subscribe(models => {
        this.models = models;
        subscriber.next(models);
        subscriber.complete();
      })
    })
  }

  getId(id: number): Observable<Model> {
    let url = this.base_url;
    return this.http.get<Model>(url.toString(), {params: {id}});
  }

  getSlug(slug: string, project_slug: string): Observable<Model> {
    let url = new URL(`${project_slug}/details/`, this.base_url);
    return new Observable<Model>(subscriber => {
      this.http.get<Model>(
        url.toString(), {params: {slug}}
      ).subscribe(model => {
        this.model = model;
        subscriber.next(model);
        subscriber.complete();
      });
    });
  }

  createEmpty(project_slug: string, model: EmptyModel): Observable<Model> {
    let url = new URL(project_slug + "/create-empty/", this.base_url);
    return this.createGeneric(url, model)
  }

  createWithSource(project_slug: string, model: GitModel): Observable<Model> {
    let url = new URL(project_slug + "/create-git/", this.base_url);
    return this.createGeneric(url, model)
  }

  createGeneric<T extends NewModel>(url: URL, new_model: T): Observable<Model> {
    return new Observable<Model>(subscriber => {
      this.http.post<Model>(url.toString(), new_model)
      .subscribe(model => {
        this.model = model;
        subscriber.next(model);
        subscriber.complete();
      });
    })
  }
}
