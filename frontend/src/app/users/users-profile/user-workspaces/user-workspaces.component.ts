/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { DisplayValueComponent } from 'src/app/helpers/display-value/display-value.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { User, UsersService, Workspace } from 'src/app/openapi';
import { UserWrapperService } from 'src/app/services/user/user.service';
@Component({
  selector: 'app-user-workspaces',
  standalone: true,
  imports: [
    CommonModule,
    MatDividerModule,
    DisplayValueComponent,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './user-workspaces.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
})
export class UserWorkspacesComponent {
  _user: User | undefined;

  workspaces: Workspace[] | undefined = undefined;

  @Input()
  set user(value: User | undefined) {
    this._user = value;
    this.reloadWorkspaces();
  }

  reloadWorkspaces() {
    this.workspaces = undefined;
    if (
      this._user === undefined ||
      this.userService.user === undefined ||
      this.userService.user.role !== 'administrator'
    )
      return;

    this.usersService.getWorkspacesForUser(this._user.id).subscribe({
      next: (workspaces) => {
        this.workspaces = workspaces;
      },
      error: () => (this.workspaces = undefined),
    });
  }

  get user(): User | undefined {
    return this._user;
  }

  constructor(
    public userService: UserWrapperService,
    private usersService: UsersService,
    private dialog: MatDialog,
    private toastService: ToastService,
  ) {}

  deleteWorkspace(workspace: Workspace) {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Delete workspace',
        text:
          `Do you really want to delete the workspace ${workspace.id} of user '${this._user!.name}'? ` +
          'This will irrevocably remove all files in the workspace.',
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.usersService
          .deleteWorkspace(workspace.id, this._user!.id)
          .subscribe({
            next: () => {
              this.toastService.showSuccess(
                'Workspace deleted successfully.',
                `The workspace ${workspace.id} of user '${this._user!.name}' was deleted.`,
              );

              this.reloadWorkspaces();
            },
          });
      }
    });
  }
}
