/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie';
import { Observable, tap } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { Project } from 'src/app/projects/service/project.service';
import { User } from 'src/app/services/user/user.service';
import { SessionHistoryService } from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-session-history/session-history.service';
import {
  ConnectionMethod,
  ToolVersionWithTool,
} from 'src/app/settings/core/tools-settings/tool.service';
import { environment } from 'src/environments/environment';

export interface Session {
  created_at: string;
  id: string;
  last_seen: string;
  type: 'persistent' | 'readonly';
  project: Project | undefined;
  version: ToolVersionWithTool | undefined;
  state: string;
  owner: User;

  download_in_progress: boolean;
  connection_method: ConnectionMethod | undefined;
}
export interface LocalStorage {
  [id: string]: string;
}

export interface Cookies {
  [id: string]: string;
}

export interface ReadonlySession extends Session {
  project: Project;
}

export const isReadonlySession = (
  session: Session,
): session is ReadonlySession => {
  return session.type === 'readonly';
};

export const isPersistentSession = (session: Session): session is Session => {
  return session.type === 'persistent';
};

export interface PathNode {
  path: string;
  name: string;
  type: 'file' | 'directory';
  isNew: boolean;
  children: PathNode[] | null;
}

export type ReadonlyModel = {
  model_slug: string;
  git_model_id: number;
  revision: string;
  deep_clone: boolean;
};

export type SessionConnectionInformation = {
  local_storage: LocalStorage;
  cookies: Cookies;
  t4c_token: string;
  redirect_url: string;
};

@Injectable({
  providedIn: 'root',
})
export class SessionService {
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService,
    private cookieService: CookieService,
    private sessionHistoryService: SessionHistoryService,
  ) {}
  BACKEND_URL_PREFIX = environment.backend_url + '/sessions';

  getCurrentSessions(): Observable<Session[]> {
    return this.http.get<Session[]>(this.BACKEND_URL_PREFIX);
  }

  createSession(
    toolId: number,
    versionId: number,
    connectionMethodId: string,
    session_type: 'persistent' | 'readonly',
    models: ReadonlyModel[],
  ): Observable<Session> {
    return this.http
      .post<Session>(`${this.BACKEND_URL_PREFIX}`, {
        tool_id: toolId,
        version_id: versionId,
        connection_method_id: connectionMethodId,
        session_type: session_type,
        provisioning: models,
      })
      .pipe(
        tap((session) => {
          if (isPersistentSession(session)) {
            this.sessionHistoryService.addSessionRequestToHistory({
              toolId,
              versionId,
              connectionMethodId,
              lastRequested: new Date(),
            });
          }
        }),
      );
  }

  getSessionConnectionInformation(
    sessionId: string,
  ): Observable<SessionConnectionInformation> {
    return this.http.get<SessionConnectionInformation>(
      `${this.BACKEND_URL_PREFIX}/${sessionId}/connection`,
    );
  }

  deleteSession(id: string): Observable<null> {
    return this.http.delete<null>(`${this.BACKEND_URL_PREFIX}/${id}`);
  }

  setConnectionInformation(
    session: Session,
    connectionInformation: SessionConnectionInformation,
  ): void {
    this.setLocalStorage(connectionInformation);
    this.setCookies(session, connectionInformation);
  }

  setLocalStorage(connectionInformation: SessionConnectionInformation): void {
    const localStorage = connectionInformation.local_storage;
    for (const key in localStorage) {
      this.localStorageService.setValue(key, localStorage[key]);
    }
  }

  setCookies(
    session: Session,
    connectionInformation: SessionConnectionInformation,
  ): void {
    const cookies = connectionInformation.cookies;
    for (const key in cookies) {
      this.cookieService.put(key, cookies[key], {
        path: `/session/${session.id}`,
        sameSite: 'strict',
      });
    }
  }

  beautifyState(state: string | undefined): SessionState {
    /* Possible states are (and a few more states):
    https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/events/event.go */

    let text = state;
    let css = 'warning';
    let success = false;
    switch (state) {
      case 'Created':
        text = 'Session created';
        css = 'warning';
        break;
      case 'Started':
        text = 'Session started';
        css = 'success';
        success = true;
        break;
      case 'Failed':
      case 'FailedCreatePodContainer':
        text = 'Failed to create session';
        css = 'error';
        break;
      case 'Killing':
        text = 'Stopping session';
        css = 'error';
        break;
      case 'Preempting':
        text = 'Session is waiting in the queue';
        css = 'error';
        break;
      case 'BackOff':
        text = 'Session crashed unexpectedly';
        css = 'error';
        break;
      case 'ExceededGracePeriod':
        text = 'The session stopped.';
        css = 'error';
        break;

      case 'FailedKillPod':
        text = 'Failed to stop session';
        css = 'error';
        break;
      case 'NetworkNotReady':
        text = 'Backend network issues';
        css = 'error';
        break;
      case 'Pulling':
        text = 'Preparation of the session';
        css = 'warning';
        break;
      case 'Pulled':
        text = 'Preparation finished';
        css = 'warning';
        break;

      // Some additional reasons that came up
      case 'Scheduled':
        text = 'Your session is scheduled';
        css = 'warning';
        break;
      case 'FailedScheduling':
        text = 'High demand. Please wait a moment.';
        css = 'warning';
        break;

      // OpenShift specific
      case 'AddedInterface':
        text = 'Preparation of the session';
        css = 'warning';
        break;

      // Pod phases (that are not handled before)
      case 'Pending':
        text = 'Your session is scheduled';
        css = 'warning';
        break;
      case 'Running':
        text = 'Session is running';
        css = 'success';
        success = true;
        break;

      // Cases for starting containers
      case 'START_LOAD_MODEL':
        text = 'Modelloading started';
        css = 'warning';
        break;
      case 'FINISH_LOAD_MODEL':
        text = 'Modelloading finished';
        css = 'warning';
        break;
      case 'FAILURE_LOAD_MODEL':
        text = 'Error during loading of the model';
        css = 'error';
        break;
      case 'START_PREPARE_WORKSPACE':
        text = 'Started workspace preparation';
        css = 'warning';
        break;
      case 'FINISH_PREPARE_WORKSPACE':
        text = 'Workspace preparation finished';
        css = 'warning';
        break;
      case 'FAILURE_PREPARE_WORKSPACE':
        text = 'Error during workspace preparation';
        css = 'error';
        break;
      case 'START_SESSION':
        text = 'Session started';
        css = 'success';
        success = true;
        break;
      case 'unknown':
      case 'Unknown':
        text = 'Unknown State';
        css = 'primary';
        break;
    }

    return {
      text: text || '',
      css: css,
      success: success,
    };
  }
}

export interface SessionState {
  text: string;
  css: string;
  success: boolean;
}
