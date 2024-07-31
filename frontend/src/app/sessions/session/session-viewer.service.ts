/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { BehaviorSubject, map } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Session, SessionConnectionInformation } from 'src/app/openapi';
import { SessionService } from 'src/app/sessions/service/session.service';

@Injectable({
  providedIn: 'root',
})
export class SessionViewerService {
  constructor(
    private sessionService: SessionService,
    private domSanitizer: DomSanitizer,
    private toastService: ToastService,
  ) {}

  private _sessions = new BehaviorSubject<ViewerSession[] | undefined>(
    undefined,
  );

  public readonly sessions$ = this._sessions.pipe(
    map((sessions) => {
      const fullscreenSession = sessions?.find((session) => session.fullscreen);
      return fullscreenSession ? [fullscreenSession] : sessions;
    }),
  );

  pushSession(
    session: Session,
    connectionInfo: SessionConnectionInformation,
  ): void {
    const viewerSession = session as ViewerSession;

    if (!connectionInfo.redirect_url) {
      this.toastService.showError(
        'Session connection information is not available yet.',
        'Try again later.',
      );
      return;
    }

    if (!connectionInfo.redirect_url) {
      this.toastService.showError(
        'Session connection information is not available yet.',
        'Try again later.',
      );
      return;
    }

    this.sessionService.setConnectionInformation(connectionInfo);
    viewerSession.focused = false;
    viewerSession.safeResourceURL =
      this.domSanitizer.bypassSecurityTrustResourceUrl(
        connectionInfo.redirect_url,
      );

    if (session.connection_method?.type === 'guacamole') {
      viewerSession.reloadToResize = true;
    } else {
      viewerSession.reloadToResize = false;
    }

    this.insertViewerSession(viewerSession);
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
        this.reloadIFrame(iframe);
      }
    });
  }

  resizeSession(session: ViewerSession): void {
    const sessionIFrame = document.querySelector<HTMLIFrameElement>(
      `iframe#session-${session.id}`,
    );

    if (sessionIFrame && session.reloadToResize) {
      this.reloadIFrame(sessionIFrame);
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
  }

  private reloadIFrame(iframe: HTMLIFrameElement) {
    const src = iframe.src;

    iframe.removeAttribute('src');

    setTimeout(() => {
      iframe.src = src;
    }, 100);
  }

  private insertViewerSession(viewerSession: ViewerSession): void {
    const currentSessions = this._sessions.value;

    if (currentSessions === undefined) {
      this._sessions.next([viewerSession]);
    } else {
      this._sessions.next([...currentSessions, viewerSession]);
    }
  }
}

export type ViewerSession = Session & {
  safeResourceURL?: SafeResourceUrl;
  focused: boolean;
  reloadToResize: boolean;
  fullscreen: boolean;
  disabled: boolean;
};
