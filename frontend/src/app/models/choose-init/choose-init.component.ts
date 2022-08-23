/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { ProjectService } from 'src/app/services/project/project.service';
import { ModelService } from 'src/app/services/model/model.service';

@Component({
  selector: 'app-choose-init',
  templateUrl: './choose-init.component.html',
  styleUrls: ['./choose-init.component.css'],
})
export class ChooseInitComponent implements OnInit {
  @Output() optionClick = new EventEmitter<string>();

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService
  ) {}

  ngOnInit(): void {}
}
