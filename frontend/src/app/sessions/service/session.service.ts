/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import {
  Session,
  SessionProvisioningRequest,
  SessionsService,
  SessionConnectionInformation,
  FileTree,
} from 'src/app/openapi';
import { SessionHistoryService } from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-session-history/session-history.service';

export const isReadonlySession = (session: Session): boolean => {
  return session.type === 'readonly';
};

export const isPersistentSession = (session: Session): boolean => {
  return session.type === 'persistent';
};

@Injectable({
  providedIn: 'root',
})
export class SessionService {
  constructor(
    private sessionHistoryService: SessionHistoryService,
    private sessionsService: SessionsService,
  ) {}

  createSession(
    toolId: number,
    versionId: number,
    connectionMethodId: string,
    session_type: 'persistent' | 'readonly',
    models: SessionProvisioningRequest[],
  ): Observable<Session> {
    return this.sessionsService
      .requestSession({
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

  setConnectionInformation(connectionInfo: SessionConnectionInformation): void {
    for (const key in connectionInfo.local_storage) {
      localStorage.setItem(key, connectionInfo.local_storage[key]);
    }
  }

  beautifyState(state: string | undefined): SessionState {
    /* Possible states are (and a few more states):
    https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/events/event.go */

    let text = state;
    let css = 'warning';
    let icon = 'pending';
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
        icon = 'check';
        break;
      case 'Failed':
      case 'FailedCreatePodContainer':
        text = 'Failed to create session';
        css = 'error';
        icon = 'error';
        break;
      case 'Killing':
        text = 'Stopping session';
        css = 'error';
        icon = 'close';
        break;
      case 'Preempting':
        text = 'Session is waiting in the queue';
        css = 'error';
        icon = 'timer_pause';
        break;
      case 'BackOff':
        text = 'Session crashed unexpectedly';
        css = 'error';
        icon = 'error';
        break;
      case 'ExceededGracePeriod':
        text = 'The session stopped.';
        css = 'error';
        icon = 'cancel';
        break;

      case 'FailedKillPod':
        text = 'Failed to stop session';
        css = 'error';
        icon = 'error';
        break;
      case 'NetworkNotReady':
        text = 'Backend network issues';
        css = 'error';
        icon = 'cloud_off';
        break;
      case 'Pulling':
        text = 'Preparation of the session';
        css = 'warning';
        icon = 'downloading';
        break;
      case 'Pulled':
        text = 'Preparation finished';
        css = 'warning';
        icon = 'download_done';
        break;

      // Some additional reasons that came up
      case 'Scheduled':
        text = 'Your session is scheduled';
        css = 'warning';
        icon = 'schedule';
        break;
      case 'FailedScheduling':
        text = 'High demand. Please wait a moment.';
        css = 'warning';
        icon = 'timer_pause';
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
        icon = 'schedule';
        break;
      case 'Running':
        text = 'Session is running';
        css = 'success';
        success = true;
        icon = 'check';
        break;

      // Cases for starting containers
      case 'START_LOAD_MODEL':
        text = 'Modelloading started';
        css = 'warning';
        icon = 'downloading';
        break;
      case 'FINISH_LOAD_MODEL':
        text = 'Modelloading finished';
        css = 'warning';
        icon = 'download_done';
        break;
      case 'FAILURE_LOAD_MODEL':
        text = 'Error during loading of the model';
        css = 'error';
        icon = 'error';
        break;
      case 'START_PREPARE_WORKSPACE':
        text = 'Started workspace preparation';
        css = 'warning';
        icon = 'downloading';
        break;
      case 'FINISH_PREPARE_WORKSPACE':
        text = 'Workspace preparation finished';
        css = 'warning';
        icon = 'download_done';
        break;
      case 'FAILURE_PREPARE_WORKSPACE':
        text = 'Error during workspace preparation';
        css = 'error';
        icon = 'error';
        break;
      case 'START_SESSION':
        text = 'Session started';
        css = 'success';
        success = true;
        icon = 'check';
        break;
      case 'NOT_FOUND':
        text = 'Session container not found';
        css = 'error';
        icon = 'error';
        break;
      case 'unknown':
      case 'Unknown':
        text = 'Unknown State';
        css = 'primary';
        icon = 'help';
        break;
    }

    return {
      text: text || '',
      css: css,
      icon: icon,
      success: success,
    };
  }
}

export interface SessionState {
  text: string;
  css: string;
  icon: string;
  success: boolean;
}

export type PathNode = Omit<FileTree, 'children'> & {
  isNew?: boolean;
  isModified?: boolean;
  isExpanded?: boolean;
  children: PathNode[] | null;
};
