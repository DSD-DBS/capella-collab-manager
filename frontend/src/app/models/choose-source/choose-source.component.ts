// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-choose-source',
  templateUrl: './choose-source.component.html',
  styleUrls: ['./choose-source.component.css'],
})
export class ChooseSourceComponent implements OnInit {
  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.modelService.init(params.project, params.model).subscribe();
    });
  }
}
