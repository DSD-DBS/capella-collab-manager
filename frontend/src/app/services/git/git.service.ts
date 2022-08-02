import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface Credentials {
  url: string;
  username: string;
  password: string;
}

export interface Instance {
  branches: string[],
  tags: string[],
}

@Injectable({
  providedIn: 'root'
})
export class GitService {

  base_url = new URL('git-utils/', environment.backend_url + '/');

  constructor(
    private http: HttpClient,
  ) { }

  instance: Instance | null = null;

  fetch(model_slug: string, credentials: Credentials): Observable<Instance> {
    let url = new URL('revisions/', this.base_url);
    return new Observable<Instance>(subscriber => {
      this.http.get<Instance>(url.toString(), {params: {
        model_slug,
        url: credentials.url,
        username: credentials.username,
        password: credentials.password,
      }}).subscribe(value => {
        this.instance = value;
        subscriber.next(value);
        subscriber.complete();
      })
    })
  }
}
