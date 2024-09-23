/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { BehaviorSubject, of, switchMap } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { DisplayValueComponent } from 'src/app/helpers/display-value/display-value.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { User, UsersService, Workspace } from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';

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
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserWorkspacesComponent implements OnInit {
  workspaces = new BehaviorSubject<Workspace[] | undefined>(undefined);

  loadWorkspaces() {
    this.workspaces.next(undefined);
    this.userWrapperService.user$
      .pipe(
        switchMap((user) => {
          if (!user) return of(undefined);
          return this.usersService.getWorkspacesForUser(user.id);
        }),
      )
      .subscribe({
        next: (workspaces) => {
          this.workspaces.next(workspaces);
        },
        error: () => this.workspaces.next(undefined),
      });
  }

  constructor(
    public ownUserService: OwnUserWrapperService,
    public userWrapperService: UserWrapperService,
    private usersService: UsersService,
    private dialog: MatDialog,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.loadWorkspaces();
  }

  deleteWorkspace(user: User, workspace: Workspace) {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Delete workspace',
        text:
          `Do you really want to delete the workspace ${workspace.id} of user '${user.name}'? ` +
          'This will irrevocably remove all files in the workspace.',
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.usersService.deleteWorkspace(workspace.id, user.id).subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Workspace deleted successfully.',
              `The workspace ${workspace.id} of user '${user.name}' was deleted.`,
            );

            this.loadWorkspaces();
          },
        });
      }
    });
  }
}
