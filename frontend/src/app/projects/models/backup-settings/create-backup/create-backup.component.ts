/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, Inject, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatCheckbox } from '@angular/material/checkbox';
import {
  MatDialogRef,
  MAT_DIALOG_DATA,
  MatDialogClose,
} from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatSelectionList, MatListOption } from '@angular/material/list';
import { UntilDestroy } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { CreateBackup, ProjectsModelsBackupsService } from 'src/app/openapi';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { MatIconComponent } from '../../../../helpers/mat-icon/mat-icon.component';

@UntilDestroy()
@Component({
  selector: 'app-create-backup',
  templateUrl: './create-backup.component.html',
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatSelectionList,
    MatListOption,
    MatIcon,
    MatCheckbox,
    MatButton,
    MatDialogClose,
    AsyncPipe,
    NgxSkeletonLoaderModule,
    MatIconComponent,
  ],
})
export class CreateBackupComponent implements OnInit {
  loading = false;

  constructor(
    public gitModelService: GitModelService,
    public t4cModelService: T4CModelService,
    @Inject(MAT_DIALOG_DATA)
    public data: { projectSlug: string; modelSlug: string },
    private pipelinesService: ProjectsModelsBackupsService,
    private dialogRef: MatDialogRef<CreateBackupComponent>,
  ) {}

  ngOnInit(): void {
    this.t4cModelService.loadT4CModels(
      this.data.projectSlug,
      this.data.modelSlug,
    );

    this.gitModelService.loadGitModels(
      this.data.projectSlug,
      this.data.modelSlug,
    );
  }

  createBackupForm = new FormGroup({
    gitmodel: new FormControl([], [this.listNotEmptyValidator()]),
    t4cmodel: new FormControl([], [this.listNotEmptyValidator()]),
    configuration: new FormGroup({
      runNightly: new FormControl(true),
    }),
  });

  listNotEmptyValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value.length) {
        return { listNotEmpty: true };
      }
      return null;
    };
  }

  createGitBackup() {
    this.loading = true;
    if (this.createBackupForm.valid) {
      const formValue = this.createBackupForm.value;
      const createBackupformValue: CreateBackup = {
        git_model_id: formValue.gitmodel![0],
        t4c_model_id: formValue.t4cmodel![0],
        include_commit_history: false,
        run_nightly: formValue.configuration!.runNightly!,
      };
      this.pipelinesService
        .createBackup(
          this.data.projectSlug,
          this.data.modelSlug,
          createBackupformValue,
        )
        .subscribe({
          next: () => {
            this.dialogRef.close(true);
            this.loading = false;
          },
          error: () => {
            this.loading = false;
          },
        });
    }
  }
}
