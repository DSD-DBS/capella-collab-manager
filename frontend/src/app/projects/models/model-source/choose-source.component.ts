/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Output } from '@angular/core';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { UserService } from 'src/app/services/user/user.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-choose-source',
  templateUrl: './choose-source.component.html',
  styleUrls: ['./choose-source.component.css'],
})
export class ChooseSourceComponent {
  @Output() modelSourceSelection = new EventEmitter<string>();

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public userService: UserService,
  ) {}
}
