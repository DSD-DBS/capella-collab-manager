/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ProjectToolsWrapperService } from 'src/app/projects/project-detail/project-tools/project-tools-wrapper.service';
import { ProjectToolsComponent } from 'src/app/projects/project-detail/project-tools/project-tools.component';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { TrainingDetailsComponent } from 'src/app/projects/project-detail/training-details/training-details.component';
import { CreateProvisionedSessionComponent } from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-provisioned-session/create-provisioned-session.component';
import { BetaTestingService } from 'src/app/users/users-profile/beta-testing/beta-testing.service';
import { CreateReadonlySessionComponent } from '../../sessions/user-sessions-wrapper/create-sessions/create-readonly-session/create-readonly-session.component';
import { ProjectWrapperService } from '../service/project.service';
import { ModelOverviewComponent } from './model-overview/model-overview.component';
import { ProjectMetadataComponent } from './project-metadata/project-metadata.component';
import { ProjectUserSettingsComponent } from './project-users/project-user-settings.component';

@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  imports: [
    ProjectMetadataComponent,
    CreateReadonlySessionComponent,
    ModelOverviewComponent,
    ProjectUserSettingsComponent,
    AsyncPipe,
    CreateProvisionedSessionComponent,
    TrainingDetailsComponent,
    ProjectToolsComponent,
  ],
})
export class ProjectDetailsComponent implements OnInit {
  constructor(
    public projectService: ProjectWrapperService,
    public projectUserService: ProjectUserService,
    public betaTestingService: BetaTestingService,
    private projectToolsWrapperService: ProjectToolsWrapperService,
  ) {}

  ngOnInit(): void {
    this.projectToolsWrapperService.loadProjectTools();
  }
}
