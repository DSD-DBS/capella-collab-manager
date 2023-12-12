/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { finalize } from 'rxjs';
import {
  T4CRepoService,
  T4CRepository,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

@Component({
  selector: 't4c-repo-deletion-dialog-dialog',
  templateUrl: './t4c-repo-deletion-dialog.component.html',
  styleUrls: ['./t4c-repo-deletion-dialog.component.css'],
})
export class T4CRepoDeletionDialogComponent {
  repositoryNameForm = new FormControl('', [
    Validators.required,
    this.repositoryNameMatchValidator(),
  ]);

  constructor(
    private repoService: T4CRepoService,
    public dialogRef: MatDialogRef<T4CRepoDeletionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public repo: T4CRepository,
  ) {}

  removeRepository(): void {
    if (this.repositoryNameForm.valid) {
      this.repoService
        .deleteRepository(this.repo.instance.id, this.repo.id)
        .pipe(
          finalize(() => {
            this.repoService.loadRepositories(this.repo.instance.id);
            this.dialogRef.close(true);
          }),
        )
        .subscribe();
    }
  }

  repositoryNameMatchValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (control.value && control.value !== this.repo.name) {
        return { repositoryNameMatchFailed: true };
      }
      return null;
    };
  }
}
