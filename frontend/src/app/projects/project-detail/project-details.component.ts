/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { CreateReadonlySessionComponent } from '../../sessions/user-sessions-wrapper/create-session/create-readonly-session/create-readonly-session.component';
import { CreateProvisionedSessionComponent } from '../../sessions/user-sessions-wrapper/create-sessions/create-provisioned-session/create-provisioned-session.component';
import { ProjectWrapperService } from '../service/project.service';
import { ModelOverviewComponent } from './model-overview/model-overview.component';
import { ProjectMetadataComponent } from './project-metadata/project-metadata.component';
import { ProjectUserSettingsComponent } from './project-users/project-user-settings.component';

@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  standalone: true,
  imports: [
    ProjectMetadataComponent,
    CreateReadonlySessionComponent,
    ModelOverviewComponent,
    ProjectUserSettingsComponent,
    AsyncPipe,
    CreateProvisionedSessionComponent,
  ],
})
export class ProjectDetailsComponent {
  constructor(
    public projectService: ProjectWrapperService,
    public projectUserService: ProjectUserService,
  ) {}
}
