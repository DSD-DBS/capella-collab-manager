import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Session, SessionsUsage } from '../../schemes';

@Injectable({
  providedIn: 'root',
})
export class SessionService {
  constructor(private http: HttpClient) {}
  BACKEND_URL_PREFIX = environment.backend_url + '/sessions/';

  getCurrentSessions(): Observable<Array<Session>> {
    return this.http.get<Array<Session>>(this.BACKEND_URL_PREFIX);
  }

  createNewSession(
    type: 'readonly' | 'persistent',
    repository: string | undefined
  ): Observable<Session> {
    return this.http.post<Session>(this.BACKEND_URL_PREFIX, {
      type,
      repository,
    });
  }

  deleteSession(id: string): Observable<any> {
    return this.http.delete<any>(this.BACKEND_URL_PREFIX + id);
  }

  getSessionsUsage(): Observable<SessionsUsage> {
    return this.http.get<SessionsUsage>(this.BACKEND_URL_PREFIX + 'usage');
  }
}
