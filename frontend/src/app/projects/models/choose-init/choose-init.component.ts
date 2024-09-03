/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgIf, AsyncPipe } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { MatIconComponent } from '../../../helpers/mat-icon/mat-icon.component';
import { ProjectWrapperService } from '../../service/project.service';

@Component({
  selector: 'app-choose-init',
  templateUrl: './choose-init.component.html',
  styleUrls: ['./choose-init.component.css'],
  standalone: true,
  imports: [NgIf, MatButton, MatIconComponent, AsyncPipe],
})
export class ChooseInitComponent {
  @Output() modelInitSelection = new EventEmitter<string>();

  constructor(
    public projectService: ProjectWrapperService,
    public modelService: ModelWrapperService,
  ) {}
}
