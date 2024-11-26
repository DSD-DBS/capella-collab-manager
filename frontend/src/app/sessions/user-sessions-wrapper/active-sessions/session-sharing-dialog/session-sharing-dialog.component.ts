/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import { Component, Inject } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { catchError, combineLatest, of, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Session, SessionsService } from 'src/app/openapi';

@Component({
  selector: 'app-session-sharing-dialog',
  imports: [
    CommonModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    FormsModule,
    ReactiveFormsModule,
    MatChipsModule,
    MatTooltipModule,
  ],
  templateUrl: './session-sharing-dialog.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
})
export class SessionSharingDialogComponent {
  form = new FormGroup({
    username: new FormControl('', [
      Validators.required,
      this.usersSelectedValidator(),
    ]),
    confirmation: new FormControl(false, Validators.requiredTrue),
  });

  loading = false;
  users: AddedUser[] = [];

  constructor(
    @Inject(MAT_DIALOG_DATA) public session: Session,
    private toastService: ToastService,
    private dialogRef: MatDialogRef<SessionSharingDialogComponent>,
    private sessionsService: SessionsService,
  ) {
    for (const session of this.session.shared_with) {
      this.users.push({
        username: session.user.name,
        state: 'success',
        tooltip: 'The session is already shared with this user.',
      });
    }
  }

  usersSelectedValidator(): ValidatorFn {
    return (_: AbstractControl): ValidationErrors | null => {
      if (this.users === undefined) {
        return null;
      }
      const users = this.users.filter((user) => user.state !== 'success');
      if (!users.length) {
        return { required: true };
      }
      return null;
    };
  }

  submit() {
    if (this.form.invalid || this.loading) {
      return;
    }

    const observables = [];
    let errorCount = 0;
    this.loading = true;

    for (const user of this.users) {
      if (user.state === 'success') {
        continue;
      }
      const username = user.username;
      observables.push(
        this.sessionsService.shareSession(this.session.id, { username }).pipe(
          tap({
            next: () => {
              this.toastService.showSuccess(
                'Session successfully shared',
                `The session has been shared with user ${username}. ` +
                  'The user should be able to see the session in their personal list of sessions.',
              );
              this.updateState(username, 'success');
              this.updateTooltip(
                username,
                'The session has been shared with the user.',
              );
            },
            error: (err) => {
              errorCount++;
              this.updateState(username, 'error');
              if (err.error.detail?.reason) {
                this.updateTooltip(username, err.error.detail?.reason);
              } else {
                this.updateTooltip(username, "The user couldn't be added.");
              }
            },
          }),
          catchError((err) => of(err)),
        ),
      );
    }

    combineLatest(observables).subscribe({
      next: () => {
        this.loading = false;
        if (errorCount == 0) {
          this.dialogRef.close();
        }
      },
    });
  }

  removeUser(username: string) {
    const index = this.users.map((user) => user.username).indexOf(username);
    if (index >= 0) {
      this.users.splice(index, 1);
    }
  }

  addUser(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();

    if (value && !this.users.find((user) => user.username === value)) {
      this.users.push({
        username: value,
        state: 'pending',
        tooltip: 'Submit the form to add the user.',
      });
    }

    event.chipInput!.clear();
  }

  updateState(username: string, state: 'success' | 'pending' | 'error') {
    const user = this.users.find((user) => user.username === username);
    if (user) {
      user.state = state;
    }
  }

  updateTooltip(username: string, tooltip: string) {
    const user = this.users.find((user) => user.username === username);
    if (user) {
      user.tooltip = tooltip;
    }
  }
}

interface AddedUser {
  username: string;
  state: 'success' | 'pending' | 'error';
  tooltip: string;
}
