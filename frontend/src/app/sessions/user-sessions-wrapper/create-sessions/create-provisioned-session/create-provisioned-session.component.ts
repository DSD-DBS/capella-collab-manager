/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { combineLatest, map, Observable, of, switchMap, take } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ModelProvisioning,
  ProjectsModelsProvisioningService,
  ProjectType,
  SessionsService,
  SessionType,
  ToolModel,
} from 'src/app/openapi';
import {
  getPrimaryGitModel,
  ModelWrapperService,
} from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { SessionService } from 'src/app/sessions/service/session.service';

@UntilDestroy()
@Component({
  selector: 'app-create-provisioned-session',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    NgxSkeletonLoaderModule,
  ],
  templateUrl: './create-provisioned-session.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
})
export class CreateProvisionedSessionComponent implements OnInit {
  constructor(
    public sessionService: SessionService,
    private router: Router,
    private modelWrapperService: ModelWrapperService,
    private provisioningService: ProjectsModelsProvisioningService,
    public projectWrapperService: ProjectWrapperService,
    private toastService: ToastService,
    private sessionsService: SessionsService,
    private dialog: MatDialog,
  ) {}

  provisioningRequestInProgress = false;

  provisioning: [ToolModel, ModelProvisioning][] | undefined = undefined;

  ngOnInit(): void {
    this.loadProvisioningInfo().subscribe((provisioning) => {
      this.provisioning = provisioning;
    });
  }

  get filteredProvisioning(): [ToolModel, ModelProvisioning][] | undefined {
    return this.provisioning?.filter(([_, provisioning]) => !!provisioning);
  }

  get projectDisplayName$(): Observable<string> {
    return this.projectWrapperService.project$.pipe(
      map((project) => {
        if (project?.type === ProjectType.Training) {
          return 'training';
        } else {
          return 'project';
        }
      }),
    );
  }

  loadProvisioningInfo() {
    return combineLatest([
      this.projectWrapperService.project$,
      this.modelWrapperService.models$,
    ]).pipe(
      switchMap(([project, models]) => {
        if (!models || !project) {
          return of(undefined);
        }
        return combineLatest(
          models.map((model) =>
            this.provisioningService
              .getProvisioning(project.slug, model.slug)
              .pipe(
                map(
                  (provisioning) =>
                    [model, provisioning] as [ToolModel, ModelProvisioning],
                ),
              ),
          ),
        );
      }),
      untilDestroyed(this),
    );
  }

  provisionWorkspace(): void {
    this.projectWrapperService.project$.pipe(take(1)).subscribe((project) => {
      this.provisioningRequestInProgress = true;
      if (!this.provisioning || !project) return;

      const requests = [];

      for (const [model, _] of this.provisioning) {
        if (!model.version) {
          this.toastService.showError(
            "Couldn't start session",
            `Could start the session for model ${model.name} because it has no version`,
          );
          continue;
        }

        const primaryGitModel = getPrimaryGitModel(model);
        if (!primaryGitModel) {
          this.toastService.showError(
            "Couldn't start session",
            `Could start the session for model ${model.name} because it has no linked Git repository`,
          );
          continue;
        }

        requests.push(
          this.sessionsService.requestSession({
            tool_id: model.tool.id,
            version_id: model.version.id,
            session_type: SessionType.Persistent,
            provisioning: [
              {
                project_slug: project.slug,
                model_slug: model.slug,
                git_model_id: primaryGitModel.id,
                deep_clone: false,
              },
            ],
          }),
        );
      }

      combineLatest(requests).subscribe({
        next: () => {
          this.provisioningRequestInProgress = false;
          this.router.navigateByUrl('/');
        },
        error: () => {
          this.provisioningRequestInProgress = false;
        },
      });
    });
  }

  resetProvisioning() {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Reset provisioning',
        text:
          'Do you really want to reset the provisioning information?' +
          ' This will reset the existing provisioned workspace to the latest state during the next session start.' +
          ' You will lose all changes made in the workspace.',
      },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (!result) return;

      this.projectWrapperService.project$.pipe(take(1)).subscribe((project) => {
        if (!this.provisioning || !project) return;
        combineLatest(
          this.provisioning.map(([model, provisioning]) => {
            if (provisioning) {
              return this.provisioningService.resetProvisioning(
                project.slug,
                model.slug,
              );
            }
            return of(undefined);
          }),
        ).subscribe(() => {
          this.toastService.showSuccess(
            'Provisioning reset successful',
            'The provisioning information has been cleared successfully. You can now start a new provisioning to fetch the latest data.',
          );
          this.loadProvisioningInfo()
            .pipe(take(1))
            .subscribe((provisioning) => (this.provisioning = provisioning));
        });
      });
    });
  }
}
