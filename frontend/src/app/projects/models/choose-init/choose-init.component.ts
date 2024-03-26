/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Output } from '@angular/core';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-choose-init',
  templateUrl: './choose-init.component.html',
})
export class ChooseInitComponent {
  @Output() modelInitSelection = new EventEmitter<string>();

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
  ) {}
}
