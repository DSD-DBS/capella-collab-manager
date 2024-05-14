/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, AsyncPipe } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { MatAnchor } from '@angular/material/button';
import { MatDivider } from '@angular/material/divider';
import { MatIcon } from '@angular/material/icon';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-choose-source',
  templateUrl: './choose-source.component.html',
  styleUrls: ['./choose-source.component.css'],
  standalone: true,
  imports: [NgIf, MatDivider, MatAnchor, MatIcon, AsyncPipe],
})
export class ChooseSourceComponent {
  @Output() modelSourceSelection = new EventEmitter<string>();

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public userService: UserWrapperService,
  ) {}
}
