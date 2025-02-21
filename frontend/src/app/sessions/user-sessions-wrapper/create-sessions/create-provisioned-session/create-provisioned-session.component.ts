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
import { combineLatest, map, Observable, of, switchMap, take, tap } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { MatIconComponent } from 'src/app/helpers/mat-icon/mat-icon.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ModelProvisioning,
  ProjectsModelsProvisioningService,
  ProjectTool,
  ProjectType,
  SessionProvisioningRequest,
  SessionsService,
  SessionType,
  SimpleToolModelWithoutProject,
} from 'src/app/openapi';
import { getPrimaryGitModel } from 'src/app/projects/models/service/model.service';
import { ProjectToolsWrapperService } from 'src/app/projects/project-detail/project-tools/project-tools-wrapper.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { RelativeTimeComponent } from '../../../../general/relative-time/relative-time.component';

@UntilDestroy()
@Component({
  selector: 'app-create-provisioned-session',
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    NgxSkeletonLoaderModule,
    MatIconComponent,
    RelativeTimeComponent,
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
    public projectWrapperService: ProjectWrapperService,
    private provisioningService: ProjectsModelsProvisioningService,
    private projectToolsWrapperService: ProjectToolsWrapperService,
    private sessionsService: SessionsService,
    private toastService: ToastService,
    private router: Router,
    private dialog: MatDialog,
  ) {}

  provisioningRequestInProgress = false;

  provisioningPerTool: ProjectToolWithProvisioning[] | undefined = undefined;
  get provisioningRequired(): boolean {
    return (
      this.provisioningPerTool?.some((tool) =>
        tool.used_by.some((model) => !model.provisioning),
      ) ?? true
    );
  }

  ngOnInit(): void {
    this.loadProvisioningInfo().subscribe();
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
      this.projectToolsWrapperService.projectTools$,
    ]).pipe(
      tap(([_, tools]) => {
        this.provisioningPerTool = tools as ProjectToolWithProvisioning[];
      }),
      switchMap(([project, tools]) => {
        if (!tools || !project) {
          return of(undefined);
        }
        return combineLatest(
          tools.map((tool) =>
            combineLatest(
              tool.used_by.map((model) =>
                this.provisioningService
                  .getProvisioning(project.slug, model.slug)
                  .pipe(
                    tap((provisioning) => {
                      const foundModel = this.provisioningPerTool
                        ?.find(
                          (provisioningTool) => provisioningTool.id === tool.id,
                        )
                        ?.used_by?.find(
                          (provisioningModel) =>
                            provisioningModel.slug === model.slug,
                        );

                      if (foundModel) {
                        foundModel.provisioning = provisioning;
                      }
                    }),
                  ),
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
      if (!this.provisioningPerTool || !project) return;
      const requests = [];
      for (const tool of this.provisioningPerTool) {
        const provisioningRequests: SessionProvisioningRequest[] = [];
        for (const model of tool.used_by) {
          const primaryGitModel = getPrimaryGitModel(model);
          if (!primaryGitModel) {
            this.toastService.showError(
              `Couldn't provision ${model.name}`,
              `It has no linked Git repository`,
            );
            continue;
          }
          provisioningRequests.push({
            project_slug: project.slug,
            model_slug: model.slug,
            git_model_id: primaryGitModel.id,
            deep_clone: true,
          });
        }

        requests.push(
          this.sessionsService.requestSession({
            tool_id: tool.tool.id,
            version_id: tool.tool_version.id,
            session_type: SessionType.Persistent,
            provisioning: provisioningRequests,
            project_slug: project.slug,
          }),
        );
      }
      combineLatest(requests).subscribe({
        next: (sessions) => {
          this.provisioningRequestInProgress = false;
          this.router.navigate(['/session-viewer'], {
            queryParams: { 'session-id': sessions.map((s) => s.id) },
          });
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
        if (!this.provisioningPerTool || !project) return;
        combineLatest(
          this.provisioningPerTool
            .map((tool) => tool.used_by)
            .flat()
            .map((model) => {
              if (model.provisioning) {
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
          this.loadProvisioningInfo().pipe(take(1)).subscribe();
        });
      });
    });
  }
}

type ModelWithProvisioning = {
  provisioning: ModelProvisioning | undefined | null;
} & SimpleToolModelWithoutProject;

type ProjectToolWithProvisioning = Omit<ProjectTool, 'used_by'> & {
  used_by: ModelWithProvisioning[];
};
