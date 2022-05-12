import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { AuthService } from '../auth/auth.service';
import { Repository } from 'src/app/schemes';

@Injectable({
  providedIn: 'root',
})
export class RepositoryService {
  constructor(private http: HttpClient, private authService: AuthService) {
    if (this.authService.isLoggedIn()) {
      this.getAndSaveManagerRole();
    }
  }
  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';
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

  createRepository(name: string): Observable<Repository> {
    return this.http.post<Repository>(this.BACKEND_URL_PREFIX, {
      name,
    });
  }

  deleteRepository(name: string): Observable<any> {
    return this.http.delete<any>(
      this.BACKEND_URL_PREFIX + name);
  }

  stageForProjectDeletion(project_name: string, username: string): Observable<any> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + project_name, { username });
  }
}