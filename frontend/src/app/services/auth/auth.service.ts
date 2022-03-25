import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { LocalStorageService } from 'src/app/auth/local-storage/local-storage.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService
  ) {}

  getRedirectURL(): Observable<GetRedirectURLResponse> {
    return this.http.get<GetRedirectURLResponse>(
      environment.backend_url + '/authentication'
    );
  }

  getAccessToken(code: string, state: string): Observable<PostTokenResponse> {
    return this.http.post<PostTokenResponse>(
      environment.backend_url + '/authentication/tokens',
      {
        code,
        state,
      }
    );
  }

  refreshToken(refresh_token: string): Observable<RefreshTokenResponse> {
    return this.http.put<PostTokenResponse>(
      environment.backend_url + '/authentication/tokens',
      { refresh_token }
    );
  }

  isLoggedIn(): boolean {
    return !!this.localStorageService.getValue('access_token');
  }

  logOut() {
    return this.http
      .get(environment.backend_url + '/authentication/logout')
      .toPromise()
      .then(() => {
        this.localStorageService.setValue('access_token', '');
        this.localStorageService.setValue('refresh_token', '');
        this.localStorageService.setValue('GUAC_AUTH', '');
      });
  }
}

export interface GetRedirectURLResponse {
  auth_url: string;
  state: string;
}

export interface PostTokenResponse {
  access_token: string;
  token_type: string;
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  refresh_token: string;
}
