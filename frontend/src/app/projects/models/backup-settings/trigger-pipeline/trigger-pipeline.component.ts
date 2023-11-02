/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { combineLatest, filter, map, switchMap, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  PipelineRun,
  PipelineRunService,
} from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import { UserService } from 'src/app/services/user/user.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { PipelineService, Pipeline } from '../service/pipeline.service';

@Component({
  selector: 'app-trigger-pipeline',
  templateUrl: './trigger-pipeline.component.html',
  styleUrls: ['./trigger-pipeline.component.css'],
})
export class TriggerPipelineComponent implements OnInit {
  projectSlug?: string = undefined;
  modelSlug?: string = undefined;

  selectedPipeline?: Pipeline = undefined;

  force = false;

  configurationForm = new FormGroup({
    includeHistory: new FormControl(false),
  });

  constructor(
    private toastService: ToastService,
    private dialogRef: MatDialogRef<TriggerPipelineComponent>,
    public dialog: MatDialog,
    public pipelineService: PipelineService,
    private pipelineRunService: PipelineRunService,
    public sessionService: SessionService,
    public userService: UserService,
    private projectService: ProjectService,
    private modelService: ModelService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    combineLatest([
      this.projectService.project$.pipe(
        filter(Boolean),
        map((project) => project.slug),
      ),
      this.modelService.model$.pipe(
        filter(Boolean),
        map((model) => model.slug),
      ),
    ]).pipe(
      tap(([projectSlug, modelSlug]) => {
        this.projectSlug = projectSlug;
        this.modelSlug = modelSlug;
      }),
      switchMap(([projectSlug, modelSlug]) =>
        this.pipelineService.loadPipelines(projectSlug, modelSlug),
      ),
    );
  }

  selectPipeline(pipeline: Pipeline) {
    this.selectedPipeline = pipeline;
  }

  runPipeline() {
    this.pipelineRunService
      .triggerRun(
        this.projectSlug!,
        this.modelSlug!,
        this.selectedPipeline!.id,
        this.configurationForm.value.includeHistory!,
      )
      .subscribe((pipelineRun: PipelineRun) => {
        this.closeDialog();
        this.router.navigate([
          'project',
          this.projectSlug,
          'model',
          this.modelSlug,
          'pipeline',
          this.selectedPipeline!.id,
          'run',
          pipelineRun.id,
          'logs',
        ]);
      });
  }

  closeDialog(): void {
    this.dialogRef.close();
  }

  removePipeline(backup: Pipeline): void {
    this.pipelineService
      .removePipeline(this.projectSlug!, this.modelSlug!, backup.id, this.force)
      .subscribe(() => {
        this.toastService.showSuccess(
          'Backup pipeline deleted',
          `The pipeline with the ID ${backup.id} has been deleted`,
        );
        this.closeDialog();
      });
  }

  openPipelineRuns(backup: Pipeline): void {
    this.closeDialog();
    this.router.navigate([
      'project',
      this.projectSlug,
      'model',
      this.modelSlug,
      'pipeline',
      backup.id,
      'runs',
    ]);
  }
}
