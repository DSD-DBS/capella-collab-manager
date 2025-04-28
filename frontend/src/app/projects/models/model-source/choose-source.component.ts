/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, EventEmitter, Output, inject } from '@angular/core';
import { MatAnchor } from '@angular/material/button';
import { MatDivider } from '@angular/material/divider';
import { MatIcon } from '@angular/material/icon';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { ProjectWrapperService } from '../../service/project.service';

@Component({
  selector: 'app-choose-source',
  templateUrl: './choose-source.component.html',
  imports: [MatDivider, MatAnchor, MatIcon, AsyncPipe],
})
export class ChooseSourceComponent {
  projectService = inject(ProjectWrapperService);
  modelService = inject(ModelWrapperService);
  userService = inject(OwnUserWrapperService);

  @Output() modelSourceSelection = new EventEmitter<string>();
}
