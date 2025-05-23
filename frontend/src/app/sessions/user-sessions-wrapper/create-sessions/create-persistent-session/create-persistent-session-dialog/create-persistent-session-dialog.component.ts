/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import {
  MAT_DIALOG_DATA,
  MatDialogClose,
  MatDialogRef,
} from '@angular/material/dialog';
import { MatRadioButton, MatRadioGroup } from '@angular/material/radio';
import { SessionType, Tool, ToolVersion } from '../../../../../openapi';
import { ConnectionMethod } from '../../../../../settings/core/tools-settings/tool.service';
import { SessionService } from '../../../../service/session.service';
import { UserSessionService } from '../../../../service/user-session.service';

export interface CreatePersistentSessionDialogData {
  tool: Tool;
  toolVersion: ToolVersion;
}

@Component({
  selector: 'app-create-persistent-session-dialog',
  imports: [
    MatRadioButton,
    MatRadioGroup,
    ReactiveFormsModule,
    FormsModule,
    MatButton,
    MatDialogClose,
  ],
  templateUrl: './create-persistent-session-dialog.component.html',
})
export class CreatePersistentSessionDialogComponent {
  private sessionService = inject(SessionService);
  private userSessionService = inject(UserSessionService);
  dialogRef =
    inject<MatDialogRef<CreatePersistentSessionDialogComponent, boolean>>(
      MatDialogRef,
    );
  data = inject<CreatePersistentSessionDialogData>(MAT_DIALOG_DATA);

  selectedConnectionMethod: ConnectionMethod;
  requestInProgress = false;

  constructor() {
    const data = this.data;

    this.selectedConnectionMethod = data.tool.config.connection.methods[0];
  }

  requestPersistentSession() {
    this.requestInProgress = true;

    this.sessionService
      .createSession({
        tool_id: this.data.tool.id,
        version_id: this.data.toolVersion.id,
        connection_method_id: this.selectedConnectionMethod.id!,
        session_type: SessionType.Persistent,
      })
      .subscribe({
        next: () => {
          this.userSessionService.loadSessions();
          this.requestInProgress = false;
          this.dialogRef.close(true);
        },
        error: () => {
          this.requestInProgress = false;
        },
      });
  }
}
