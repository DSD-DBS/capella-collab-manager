// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ProjectService } from 'src/app/services/project/project.service';
import { ModelService } from 'src/app/services/model/model.service';

@Component({
  selector: 'app-choose-source',
  templateUrl: './choose-source.component.html',
  styleUrls: ['./choose-source.component.css'],
})
export class ChooseSourceComponent implements OnInit {
  constructor(
    public projectService: ProjectService,
    public modelService: ModelService
  ) {}

  ngOnInit(): void {}
}
