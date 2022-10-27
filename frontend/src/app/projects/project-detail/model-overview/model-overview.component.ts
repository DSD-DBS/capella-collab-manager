/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { Model, ModelService } from 'src/app/services/model/model.service';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';
import { SessionService } from '../../../services/session/session.service';

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

  requestSession(model: Model) {
    if (!model.version) {
      return;
    }
    this.sessionService
      .createReadonlySession(this.project.slug, model.version.id)
      .subscribe(() => {
        this.router.navigateByUrl('/');
      });
  }
}
