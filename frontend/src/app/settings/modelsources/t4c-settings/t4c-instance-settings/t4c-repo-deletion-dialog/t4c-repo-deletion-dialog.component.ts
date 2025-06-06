/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  ValidationErrors,
  ValidatorFn,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { finalize } from 'rxjs';
import {
  ExtendedT4CRepository,
  T4CRepositoryWrapperService,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

@Component({
  selector: 't4c-repo-deletion-dialog-dialog',
  templateUrl: './t4c-repo-deletion-dialog.component.html',
  imports: [
    FormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    ReactiveFormsModule,
    MatError,
    MatButton,
  ],
})
export class T4CRepoDeletionDialogComponent {
  private repoService = inject(T4CRepositoryWrapperService);
  dialogRef =
    inject<MatDialogRef<T4CRepoDeletionDialogComponent>>(MatDialogRef);
  repo = inject<ExtendedT4CRepository>(MAT_DIALOG_DATA);

  repositoryNameForm = new FormControl('', [
    Validators.required,
    this.repositoryNameMatchValidator(),
  ]);

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
