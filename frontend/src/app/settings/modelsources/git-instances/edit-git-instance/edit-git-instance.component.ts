/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import {
  FormBuilder,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { GitInstance, PostGitInstance } from 'src/app/openapi';
import { GitInstancesWrapperService } from 'src/app/settings/modelsources/git-instances/service/git-instances.service';

@UntilDestroy()
@Component({
  selector: 'app-edit-git-instance',
  templateUrl: './edit-git-instance.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatSelect,
    MatOption,
    MatInput,
    MatButton,
    AsyncPipe,
    MatIconModule,
  ],
})
export class EditGitInstanceComponent implements OnInit, OnDestroy {
  gitInstanceForm = this.fb.group({
    type: ['', Validators.required],
    name: ['', Validators.required],
    url: ['', Validators.required],
    api_url: [''],
  });

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    public gitInstancesService: GitInstancesWrapperService,
    private breadcrumbsService: BreadcrumbsService,
    private fb: FormBuilder,
    private dialog: MatDialog,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.gitInstancesService.gitInstance$
      .pipe(filter(Boolean), untilDestroyed(this))
      .subscribe((instance: GitInstance) => {
        this.gitInstanceForm.controls.name.addAsyncValidators(
          this.gitInstancesService.asyncNameValidator(instance),
        );

        this.gitInstanceForm.patchValue(instance);
        this.breadcrumbsService.updatePlaceholder({ gitInstance: instance });
      });

    this.route.params
      .pipe(
        untilDestroyed(this),
        map((params) => parseInt(params.id)),
      )
      .subscribe((instanceId) => {
        this.gitInstancesService.loadGitInstanceById(instanceId);
      });

    this.gitInstancesService.loadGitInstances();
  }

  ngOnDestroy(): void {
    this.breadcrumbsService.updatePlaceholder({ gitInstance: undefined });
  }

  editGitInstance(gitInstanceID: number): void {
    this.gitInstancesService
      .editGitInstance(
        gitInstanceID,
        this.gitInstanceForm.value as PostGitInstance,
      )
      .subscribe(() => {
        this.router.navigate(['../../git-instances'], {
          relativeTo: this.route,
        });
        this.toastService.showSuccess(
          '',
          'Git Server Instance updated successfully',
        );
      });
  }

  deleteGitInstance(gitInstance: GitInstance): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Delete Git Instance',
        text: `Do you really want to delete the Git instance '${gitInstance.name}' with ID '${gitInstance.id}'?`,
      },
    });

    dialogRef.afterClosed().subscribe((response) => {
      if (response) {
        this.gitInstancesService
          .deleteGitInstance(gitInstance.id)
          .subscribe(() => {
            this.router.navigate(['../../git-instances'], {
              relativeTo: this.route,
            });
            this.toastService.showSuccess(
              '',
              `Git Server Instance '${gitInstance.name}' remoted successfully`,
            );
          });
      }
    });
  }
}
