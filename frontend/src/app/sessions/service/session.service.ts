/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Session } from 'src/app/schemes';
import { environment } from 'src/environments/environment';

export type ReadonlyModel = {
  model_slug: string;
  git_model_id: number;
  revision: string;
  deep_clone: boolean;
};

@Injectable({
  providedIn: 'root',
})
export class SessionService {
  constructor(private http: HttpClient) {}
  BACKEND_URL_PREFIX = environment.backend_url + '/sessions/';

  getCurrentSessions(): Observable<Session[]> {
    return this.http.get<Session[]>(this.BACKEND_URL_PREFIX);
  }

  createReadonlySession(
    project_slug: string,
    models: ReadonlyModel[]
  ): Observable<Session> {
    return this.http.post<Session>(
      `${environment.backend_url}/projects/${project_slug}/sessions/readonly`,
      {
        models: models,
      }
    );
  }

  createPersistentSession(
    toolId: number,
    versionId: number
  ): Observable<Session> {
    return this.http.post<Session>(`${this.BACKEND_URL_PREFIX}persistent`, {
      tool_id: toolId,
      version_id: versionId,
    });
  }

  deleteSession(id: string): Observable<any> {
    return this.http.delete<any>(this.BACKEND_URL_PREFIX + id);
  }

  beautifyState(state: string | undefined): SessionState {
    /* Possible states are (and a few more states):
    https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/events/event.go */

    let text = state;
    let css = 'warning';
    let success = false;
    switch (state) {
      case 'Created':
        text = 'Created session';
        css = 'warning';
        break;
      case 'Started':
        text = 'Started session';
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

      // Cases for readonly containers
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
