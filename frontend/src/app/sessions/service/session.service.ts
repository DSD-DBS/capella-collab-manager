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
  SessionPreparationState,
  SessionState,
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

  beautifyState(
    preparationState: SessionPreparationState,
    state: SessionState,
  ): DisplaySessionState {
    if (
      preparationState === SessionPreparationState.NotFound ||
      state === SessionState.NotFound
    ) {
      return {
        text: 'Session not found',
        css: 'error',
        icon: 'error',
        success: false,
      };
    }
    switch (preparationState) {
      case SessionPreparationState.Pending:
        return {
          text: 'Session preparation is pending',
          css: 'warning',
          icon: 'timer',
          success: false,
        };
      case SessionPreparationState.Failed:
        return {
          text: 'Session preparation failed',
          info: [
            'The session preparation has failed. We will not continue to start the session.',
            'A failed preparation usually indicates a failed provisioning,',
            'e. g., due to an unreachable Git Server or invalid credentials.',
            'Contact support for more details.',
          ].join(' '),
          css: 'error',
          icon: 'error',
          success: false,
        };
      case SessionPreparationState.Running:
        return {
          text: 'Session preparation is running',
          info: 'During session preparation, we provision the workspace and configure the environment.',
          css: 'warning',
          icon: 'timer',
          success: false,
        };
      case SessionPreparationState.Completed:
        // Switch to session state

        switch (state) {
          case SessionState.Running:
            return {
              text: 'Session is up & running',
              css: 'success',
              icon: 'check',
              success: true,
            };
          case SessionState.Terminated:
            return {
              text: 'Session is terminated',
              info: [
                "The session is terminated and can't be accessed anymore.",
                'Request a new session or contact support for further information.',
              ].join(' '),
              css: 'error',
              icon: 'close',
              success: false,
            };
          case SessionState.Pending:
            return {
              text: 'Session is pending',
              info: [
                'The session preparation is completed, but the session is pending.',
                'Depending on the load and the infrastructure, it may take until all necessary information for the session is available.',
                'Take a moment to make some tea and return shortly.',
              ].join(' '),
              css: 'warning',
              icon: 'hourglass',
              success: false,
            };
          case SessionState.Failed:
            return {
              text: 'Session startup has failed',
              info: [
                'The session preparation was completed, but the session startup did fail.',
                'This should not happen. Contact support for help.',
              ].join(' '),
              css: 'error',
              icon: 'error',
              success: false,
            };
        }
    }

    return {
      text: 'Session state is unknown',
      info: [
        "We're not sure what happened here.",
        "Contact support if the state doesn't change.",
      ].join(' '),
      css: 'primary',
      icon: 'help',
      success: false,
    };
  }
}

export interface DisplaySessionState {
  text: string;
  info?: string | undefined;
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
