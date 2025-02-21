/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  inject,
  model,
  OnInit,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { UntilDestroy } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderComponent } from 'ngx-skeleton-loader';
import { filter, switchMap, take } from 'rxjs';
import { RelativeTimeComponent } from 'src/app/general/relative-time/relative-time.component';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ProjectsVolumesService, ProjectVolume } from 'src/app/openapi';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-volumes',
  imports: [
    MatTooltipModule,
    MatIconModule,
    NgxSkeletonLoaderComponent,
    AsyncPipe,
    MatButtonModule,
    RelativeTimeComponent,
  ],
  templateUrl: './project-volumes.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectVolumesComponent implements OnInit {
  private projectVolumeService = inject(ProjectsVolumesService);
  public projectWrapperService = inject(ProjectWrapperService);
  public projectUserService = inject(ProjectUserService);
  private matDialog = inject(MatDialog);

  projectVolume = model<ProjectVolume | null | undefined>(undefined);
  volumeCreationInProgress = model<boolean>(false);

  ngOnInit(): void {
    this.reloadVolumes();
  }

  reloadVolumes() {
    this.projectWrapperService.project$
      .pipe(
        filter(Boolean),
        take(1),
        switchMap((project) =>
          this.projectVolumeService.getProjectVolume(project.slug),
        ),
      )
      .subscribe((volume) => {
        this.projectVolume.set(volume);
      });
  }

  addVolume() {
    this.volumeCreationInProgress.set(true);
    this.projectWrapperService.project$
      .pipe(
        filter(Boolean),
        take(1),
        switchMap((project) =>
          this.projectVolumeService.createProjectVolume(project.slug),
        ),
      )
      .subscribe({
        next: () => {
          this.volumeCreationInProgress.set(false);
          this.reloadVolumes();
        },
        error: () => {
          this.volumeCreationInProgress.set(false);
        },
      });
  }

  deleteVolume(projectVolume: ProjectVolume) {
    this.projectWrapperService.project$
      .pipe(filter(Boolean), take(1))
      .subscribe((project) => {
        this.matDialog
          .open(ConfirmationDialogComponent, {
            data: {
              title: 'Remove project volume',
              text: `Do you want to delete the project volume of the project ${project.name}? This will irrevocably delete all files in the workspace.`,
            },
          })
          .afterClosed()
          .subscribe((result) => {
            if (result) {
              this.projectVolumeService
                .deleteProjectVolume(project.slug, projectVolume.id)
                .subscribe({
                  next: () => {
                    this.reloadVolumes();
                  },
                });
            }
          });
      });
  }
}
