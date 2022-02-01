import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { LocalStorageService } from 'src/app/auth/local-storage/local-storage.service';
import { Session, User } from 'src/app/schemes';
import { environment } from 'src/environments/environment';
import { AuthService } from '../auth/auth.service';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  user: User | undefined = undefined;

  BACKEND_URL_PREFIX = environment.backend_url + '/users/';
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService,
    private authService: AuthService
  ) {
    if (this.authService.isLoggedIn()) {
      this.getAndSaveOwnUser();
    }
  }

  getAndSaveOwnUser(): void {
    this.getUser(this.getUsernameFromLocalStorage()).subscribe((res) => {
      this.user = res;
    });
  }

  getUser(username: string): Observable<User> {
    return this.http.get<User>(this.BACKEND_URL_PREFIX + username);
  }

  deleteUser(username: string): Observable<any> {
    return this.http.delete<any>(this.BACKEND_URL_PREFIX + username);
  }

  getUsers(): Observable<Array<User>> {
    return this.http.get<Array<User>>(this.BACKEND_URL_PREFIX);
  }

  getUsernameFromLocalStorage(): string {
    return JSON.parse(
      atob(this.localStorageService.getValue('access_token').split('.')[1])
    )['preferred_username'];
  }

  getOwnActiveSessions(): Observable<Array<Session>> {
    return this.http.get<Array<Session>>(
      this.BACKEND_URL_PREFIX +
        this.getUsernameFromLocalStorage() +
        '/sessions/'
    );
  }

  updateRoleOfUser(
    username: string,
    role: 'user' | 'administrator'
  ): Observable<User> {
    return this.http.patch<User>(
      this.BACKEND_URL_PREFIX + username + '/roles',
      {
        role,
      }
    );
  }
}
