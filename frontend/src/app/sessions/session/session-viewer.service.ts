/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import {
  BehaviorSubject,
  map,
  Subscription,
  switchMap,
  takeWhile,
  timer,
} from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Session,
  SessionConnectionInformation,
  SessionsService,
} from 'src/app/openapi';
import { SessionService } from 'src/app/sessions/service/session.service';

@Injectable({
  providedIn: 'root',
})
export class SessionViewerService {
  private sessionService = inject(SessionService);
  private domSanitizer = inject(DomSanitizer);
  private toastService = inject(ToastService);
  private sessionsService = inject(SessionsService);

  constructor() {
    window.addEventListener('message', (event) => {
      if (event.origin !== window.location.origin) {
        return;
      }

      if (event.data.type === 'setFullscreen') {
        const session = this._sessions.value?.find(
          (session) => session.id === event.data.sessionId,
        );

        if (session && event.data.fullscreen !== session.fullscreen) {
          this.toggleFullscreen(session);
        }
      }
    });
  }

  private _sessions = new BehaviorSubject<ViewerSession[] | undefined>(
    undefined,
  );

  public readonly sessions$ = this._sessions.pipe(
    map((sessions) => {
      const fullscreenSession = sessions?.find((session) => session.fullscreen);
      return fullscreenSession ? [fullscreenSession] : sessions;
    }),
  );

  public readonly allSessions$ = this._sessions.asObservable();

  private _subscriptions: Subscription[] = [];

  pushSession(sessionID: string): void {
    this._subscriptions.push(
      timer(0, 3000)
        .pipe(
          switchMap(() => this.sessionsService.getSession(sessionID)),
          map(
            (session) =>
              [
                session,
                this.sessionService.beautifyState(
                  session.preparation_state,
                  session.state,
                ).success,
              ] as [Session, boolean],
          ),
          takeWhile(([_, success]) => !success, true),
        )
        .subscribe(([session, success]) => {
          if (success) {
            this.sessionsService
              .getSessionConnectionInformation(session.id)
              .subscribe((connectionInfo) => {
                this._connectToSession(session, connectionInfo.payload);
              });
          } else {
            this.updateOrInsertSession(session);
          }
        }),
    );
  }

  private _connectToSession(
    session: Session,
    connectionInfo: SessionConnectionInformation,
  ): void {
    this.sessionService.setConnectionInformation(connectionInfo);

    if (!connectionInfo.redirect_url) {
      this.toastService.showError(
        'Session connection information is not available.',
        'Contact support for more details.',
      );
      return;
    }

    this.updateOrInsertSession(session, connectionInfo);
  }

  focusSession(session: Session): void {
    document.getElementById('session-' + session.id)?.focus();

    const updatedSessions = this._sessions.value?.map((curSession) => ({
      ...curSession,
      focused: session.id === curSession.id,
    }));

    this._sessions.next(updatedSessions);
  }

  disableAllSessions(): void {
    this._sessions.next(
      this._sessions.value?.map((curSession) => ({
        ...curSession,
        disabled: true,
      })),
    );
  }

  enableAllSessions(): void {
    this._sessions.next(
      this._sessions.value?.map((curSession) => ({
        ...curSession,
        disabled: false,
      })),
    );
  }

  resizeSessions(): void {
    document.querySelectorAll('iframe').forEach((iframe) => {
      const session = this._sessions.value?.find(
        (session) => `session-${session.id}` === iframe.id,
      );

      if (session?.reloadToResize) {
        this._reloadIFrame(iframe);
      }
    });
  }

  resizeSession(session: ViewerSession): void {
    const sessionIFrame = document.querySelector<HTMLIFrameElement>(
      `iframe#session-${session.id}`,
    );

    if (sessionIFrame && session.reloadToResize) {
      this._reloadIFrame(sessionIFrame);
    }
  }

  toggleFullscreen(session: ViewerSession): void {
    const updatedSessions = this._sessions.value?.map((curSession) => {
      if (session.id === curSession.id) {
        return { ...curSession, fullscreen: !curSession.fullscreen };
      }
      return curSession;
    });
    this._sessions.next(updatedSessions);
    this.resizeSession(session);
  }

  clearSessions(): void {
    this._sessions.next(undefined);
    this._subscriptions.forEach((s) => s.unsubscribe());
  }

  private _reloadIFrame(iframe: HTMLIFrameElement) {
    const src = iframe.src;

    iframe.removeAttribute('src');

    setTimeout(() => {
      iframe.src = src;
    }, 100);
  }

  private updateOrInsertSession(
    session: Session,
    connectionInfo?: SessionConnectionInformation,
  ): void {
    const currentSessions = this._sessions.value;

    let safeResourceURL: SafeResourceUrl | undefined;
    if (connectionInfo?.redirect_url) {
      safeResourceURL = this.domSanitizer.bypassSecurityTrustResourceUrl(
        connectionInfo.redirect_url,
      );
    }

    const viewerSession: ViewerSession = {
      ...session,
      focused: false,
      safeResourceURL: safeResourceURL,
      reloadToResize: false,
      fullscreen: false,
      disabled: false,
      connectionInfo: connectionInfo,
    };

    if (session.connection_method?.type === 'guacamole') {
      viewerSession.reloadToResize = true;
    }

    if (currentSessions === undefined) {
      viewerSession.focused = true;

      this._sessions.next([viewerSession]);
    } else {
      const index = currentSessions.findIndex(
        (session) => session.id === viewerSession.id,
      );
      if (index === -1) {
        this._sessions.next([...currentSessions, viewerSession]);
      } else {
        currentSessions[index] = {
          ...currentSessions[index],
          ...session,
          safeResourceURL,
          connectionInfo,
        };
        this._sessions.next(currentSessions);
      }
    }
  }
}

export type ViewerSession = Session & {
  safeResourceURL?: SafeResourceUrl;
  focused: boolean;
  reloadToResize: boolean;
  fullscreen: boolean;
  disabled: boolean;
  connectionInfo?: SessionConnectionInformation;
};
