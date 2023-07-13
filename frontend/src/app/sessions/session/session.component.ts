/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { take } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { Session } from 'src/app/schemes';
import { GuacamoleService } from 'src/app/services/guacamole/guacamole.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';

@Component({
  selector: 'app-session',
  templateUrl: './session.component.html',
  styleUrls: ['./session.component.css'],
})
export class SessionComponent {
  cachedSessions: Session[] = [];
  selectedSessions: Session[] = [];

  constructor(
    public userSessionService: UserSessionService,
    private guacamoleService: GuacamoleService,
    private localStorageService: LocalStorageService,
    private domSanitizer: DomSanitizer
  ) {
    this.userSessionService.loadSessions();
  }

  selectSessions() {
    this.userSessionService.sessions$.pipe(take(1)).subscribe((sessions) => {
      for (const session of sessions!) {
        if (session.jupyter_uri) {
          session.safeResourceURL =
            this.domSanitizer.bypassSecurityTrustResourceUrl(
              session.jupyter_uri
            );
          this.selectedSessions.push(session);
        } else {
          this.guacamoleService
            .getGucamoleToken(session?.id)
            .subscribe((res) => {
              this.localStorageService.setValue('GUAC_AUTH', res.token);
              session.safeResourceURL =
                this.domSanitizer.bypassSecurityTrustResourceUrl(res.url);
              this.selectedSessions.push(session);
            });
        }
      }
    });
  }
}
