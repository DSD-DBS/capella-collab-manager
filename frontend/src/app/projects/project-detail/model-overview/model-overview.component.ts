/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { Model, ModelService } from 'src/app/services/model/model.service';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';
import { SessionService } from 'src/app/services/session/session.service';
import { TriggerPipelineComponent } from '../../models/backup-settings/trigger-pipeline/trigger-pipeline.component';

@Component({
  selector: 'app-model-overview',
  templateUrl: './model-overview.component.html',
  styleUrls: ['./model-overview.component.css'],
})
export class ModelOverviewComponent implements OnInit {
  @Input() project!: Project;
  models?: Model[];

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    private dialog: MatDialog,
    public sessionService: SessionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.modelService._models.pipe().subscribe((models) => {
      this.models = models;
    });
  }

  getPrimaryWorkingMode(model: Model): string {
    if (model.t4c_models.length) {
      return 'T4C';
    } else if (model.git_models.length) {
      return 'Git';
    }
    return 'Unset';
  }

  requestSession(model: Model): void {
    if (!model.version) {
      return;
    }
    this.sessionService
      .createReadonlySession(this.project.slug, model.slug)
      .subscribe(() => {
        this.router.navigateByUrl('/');
      });
  }

  openPipelineDialog(model: Model): void {
    this.dialog.open(TriggerPipelineComponent, {
      data: model,
    });
  }
}
