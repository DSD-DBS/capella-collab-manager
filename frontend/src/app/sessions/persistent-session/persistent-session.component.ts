/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { Session } from 'src/app/schemes';
import {
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';
import { SessionService } from '../service/session.service';
import { UserSessionService } from '../service/user-session.service';

@Component({
  selector: 'app-persistent-session',
  templateUrl: './persistent-session.component.html',
  styleUrls: ['./persistent-session.component.css'],
})
export class PersistentSessionComponent implements OnInit, OnDestroy {
  persistenSession?: Session = undefined;
  private persistentSessionsSubscription?: Subscription;

  versions: ToolVersion[] = [];

  public form = new FormGroup({
    toolId: new FormControl(null, Validators.required),
    versionId: new FormControl(null, Validators.required),
  });

  constructor(
    public toolService: ToolService,
    private sessionService: SessionService,
    private userSessionService: UserSessionService
  ) {}

  ngOnInit(): void {
    this.toolService.getTools().subscribe();

    this.persistentSessionsSubscription =
      this.userSessionService.persistentSessions.subscribe(
        (sessions) => (this.persistenSession = sessions?.at(0))
      );
  }

  ngOnDestroy(): void {
    this.persistentSessionsSubscription?.unsubscribe();
  }

  requestPersistentSession() {
    if (!this.form.valid && !this.persistenSession) {
      return;
    }

    this.sessionService
      .createPersistentSession(
        this.form.controls.toolId.value!,
        this.form.controls.versionId.value!
      )
      .subscribe(() => this.userSessionService.loadSessions());
  }

  getVersionsForTool(toolId: number): void {
    this.versions = [];
    this.toolService
      .getVersionsForTool(toolId)
      .subscribe((res: ToolVersion[]) => {
        this.versions = res;
      });
  }
}
