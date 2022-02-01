import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { AuthService } from '../auth/auth.service';

@Injectable({
  providedIn: 'root',
})
export class RepositoryService {
  constructor(private http: HttpClient, private authService: AuthService) {
    if (this.authService.isLoggedIn()) {
      this.getAndSaveManagerRole();
    }
  }
  BACKEND_URL_PREFIX = environment.backend_url + '/repositories/';
  isManager: boolean = false;
  repositories: Array<Repository> = [];

  getAndSaveManagerRole(): void {
    this.getRepositories().subscribe((res: Array<Repository>) => {
      let tmpIsManager = false;
      for (let s of res) {
        if (s.role === 'administrator' || s.role === 'manager') {
          tmpIsManager = true;
        }
      }
      this.isManager = tmpIsManager;
    });
  }

  getRepositories(): Observable<Array<Repository>> {
    return this.http.get<Array<Repository>>(this.BACKEND_URL_PREFIX);
  }

  refreshRepositories(): void {
    this.getRepositories().subscribe((res) => {
      this.repositories = res;
    });
  }
}

export type Warnings = 'LICENCE_LIMIT' | 'NO_GIT_MODEL_DEFINED';

export interface Repository {
  repository_name: string;
  username: string;
  permissions: Array<'read' | 'write'>;
  warnings: Array<Warnings>;
  role: 'user' | 'manager' | 'administrator';
}
