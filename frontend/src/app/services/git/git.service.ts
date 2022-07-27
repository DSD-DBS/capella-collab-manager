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
  url: string;
  username: string;
  password: string;
  revisions: {
    branches: string[],
    tags: string[],
  }
}

@Injectable({
  providedIn: 'root'
})
export class GitService {

  base_url = new URL('git-credentials/', environment.backend_url + '/');

  constructor(
    private http: HttpClient,
  ) { }

  instance: Instance | null = null;

  fetch(credentials: Credentials): Observable<Instance> {
    let mock = {
      ...credentials,
      revisions: {
        branches: ['main', 'master', 'staging'],
        tags: ['v0.1', 'v1.0', 'v1.2'],
      }
    }
    return of(mock)

    let url = new URL('fetch/', this.base_url);
    this.http.get<Instance>(url.toString(), {params: {...credentials}})
    .subscribe(instance => {
      this.instance = instance;
      return instance;
    })
  }
}
