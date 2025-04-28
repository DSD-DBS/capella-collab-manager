/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { BehaviorSubject, of, switchMap } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { User, UsersWorkspacesService, Workspace } from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';

@Component({
  selector: 'app-user-workspaces',
  imports: [CommonModule, MatDividerModule, MatButtonModule, MatIconModule],
  templateUrl: './user-workspaces.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserWorkspacesComponent implements OnInit {
  ownUserService = inject(OwnUserWrapperService);
  userWrapperService = inject(UserWrapperService);
  private usersWorkspaceService = inject(UsersWorkspacesService);
  private dialog = inject(MatDialog);
  private toastService = inject(ToastService);

  workspaces = new BehaviorSubject<Workspace[] | undefined>(undefined);

  loadWorkspaces() {
    this.workspaces.next(undefined);
    this.userWrapperService.user$
      .pipe(
        switchMap((user) => {
          if (!user) return of(undefined);
          return this.usersWorkspaceService.getWorkspacesForUser(user.id);
        }),
      )
      .subscribe({
        next: (workspaces) => {
          this.workspaces.next(workspaces);
        },
        error: () => this.workspaces.next(undefined),
      });
  }

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
        this.usersWorkspaceService
          .deleteWorkspace(workspace.id, user.id)
          .subscribe({
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
