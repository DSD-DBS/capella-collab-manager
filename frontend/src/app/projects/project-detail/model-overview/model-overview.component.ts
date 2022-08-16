// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Input, OnInit } from '@angular/core';
import { IntegrationService } from 'src/app/integrations/integration.service';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-model-overview',
  templateUrl: './model-overview.component.html',
  styleUrls: ['./model-overview.component.css'],
})
export class ModelOverviewComponent implements OnInit {
  @Input()
  project_slug = '';

  constructor(
    public integrations: IntegrationService,
    public projectService: ProjectService,
    public modelService: ModelService
  ) {}

  ngOnInit(): void {
    this.modelService.initAll(this.project_slug).subscribe();
  }
}
