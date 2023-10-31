/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { MatLegacyCheckboxChange as MatCheckboxChange } from '@angular/material/legacy-checkbox';
import { DomSanitizer } from '@angular/platform-browser';
import { filter, take } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { Session } from 'src/app/schemes';
import { GuacamoleService } from 'src/app/services/guacamole/guacamole.service';
import { FullscreenService } from 'src/app/sessions/service/fullscreen.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';

@Component({
  selector: 'app-session',
  templateUrl: './session.component.html',
})
export class SessionComponent implements OnInit {
  cachedSessions?: CachedSession[] = undefined;

  selectedSessions: Session[] = [];
  selectedWindowType: string = 'floating';

  constructor(
    public userSessionService: UserSessionService,
    public sessionService: SessionService,
    public fullscreenService: FullscreenService,
    private guacamoleService: GuacamoleService,
    private localStorageService: LocalStorageService,
    private domSanitizer: DomSanitizer,
  ) {
    this.userSessionService.loadSessions();
  }

  get checkedSessions(): undefined | CachedSession[] {
    return this.cachedSessions?.filter((session) => session.checked);
  }

  get isTailingWindow(): boolean {
    return this.selectedWindowType === 'tailing';
  }

  get isFloatingWindow() {
    return this.selectedWindowType === 'floating';
  }

  changeSessionSelection(event: MatCheckboxChange, session: CachedSession) {
    session.checked = event.checked;
  }

  ngOnInit(): void {
    this.initializeCachedSessions();
  }

  initializeCachedSessions() {
    this.userSessionService.sessions$
      .pipe(
        filter((sessions) => sessions !== undefined),
        take(1),
      )
      .subscribe((sessions) => {
        this.cachedSessions = sessions?.map((session) => {
          (session as CachedSession).checked = false;
          return session;
        });
      });
  }

  selectSessions() {
    this.checkedSessions?.forEach((session) => {
      session.focused = false;
      if (session.jupyter_uri) {
        session.safeResourceURL =
          this.domSanitizer.bypassSecurityTrustResourceUrl(session.jupyter_uri);
        session.reloadToResize = false;
        this.selectedSessions.push(session);
      } else {
        this.guacamoleService.getGucamoleToken(session?.id).subscribe((res) => {
          this.localStorageService.setValue('GUAC_AUTH', res.token);
          session.safeResourceURL =
            this.domSanitizer.bypassSecurityTrustResourceUrl(res.url);
          session.reloadToResize = true;
          this.selectedSessions.push(session);
        });
      }
    });
  }
}

type CachedSession = Session & {
  checked?: boolean;
};
