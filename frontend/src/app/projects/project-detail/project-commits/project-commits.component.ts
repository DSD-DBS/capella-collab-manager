/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';

@Component({
  selector: 'app-project-commits',
  templateUrl: './project-commits.component.html',
})
export class ProjectCommitsComponent implements OnInit {
  models?: Model[];

  constructor(public modelService: ModelService) {}

  ngOnInit(): void {
    this.modelService.models$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((models) => (this.models = models));
  }
}
