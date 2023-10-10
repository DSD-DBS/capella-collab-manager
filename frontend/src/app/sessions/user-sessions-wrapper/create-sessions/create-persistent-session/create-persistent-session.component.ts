/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { Session } from 'src/app/schemes';
import { SessionService } from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';
import {
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';

@UntilDestroy()
@Component({
  selector: 'app-create-persistent-session',
  templateUrl: './create-persistent-session.component.html',
  styleUrls: ['./create-persistent-session.component.css'],
})
export class CreatePersistentSessionComponent implements OnInit {
  persistentSession?: Session;

  versions: ToolVersion[] = [];

  public toolSelectionForm = new FormGroup({
    toolId: new FormControl(null, Validators.required),
    versionId: new FormControl<number | null>(null, Validators.required),
  });

  constructor(
    public toolService: ToolService,
    private sessionService: SessionService,
    private userSessionService: UserSessionService,
  ) {}

  ngOnInit(): void {
    this.toolService.getTools().subscribe();

    this.userSessionService.persistentSessions$
      .pipe(untilDestroyed(this))
      .subscribe((sessions) => (this.persistentSession = sessions?.at(0)));
  }

  requestPersistentSession() {
    if (!this.toolSelectionForm.valid && !this.persistentSession) {
      return;
    }

    this.sessionService
      .createPersistentSession(
        this.toolSelectionForm.controls.toolId.value!,
        this.toolSelectionForm.controls.versionId.value!,
      )
      .subscribe(() => this.userSessionService.loadSessions());
  }

  getVersionsForTool(toolId: number): void {
    this.versions = [];
    this.toolService
      .getVersionsForTool(toolId)
      .subscribe((res: ToolVersion[]) => {
        this.versions = res;
        if (res.length) {
          this.toolSelectionForm.controls.versionId.setValue(
            (res.filter((value) => value.is_recommended).at(0) || res[0]).id,
          );
        }
      });
  }
}
