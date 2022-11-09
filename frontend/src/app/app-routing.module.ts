/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuardService } from './general/auth/auth-guard/auth-guard.service';
import { AuthRedirectComponent } from './general/auth/auth-redirect/auth-redirect.component';
import { AuthComponent } from './general/auth/auth/auth.component';
import { LogoutRedirectComponent } from './general/auth/logout/logout-redirect/logout-redirect.component';
import { LogoutComponent } from './general/auth/logout/logout/logout.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { AddT4cSourceComponent } from './projects/models/add-t4c-source/add-t4c-source.component';
import { CreateCoworkingMethodComponent } from './projects/models/create-coworking-method/create-coworking-method.component';
import { CreateModelComponent } from './projects/models/create-model/create-model.component';
import { ModelDetailComponent } from './projects/models/model-detail/model-detail.component';
import { T4cModelWrapperComponent } from './projects/models/model-detail/t4c-model-wrapper/t4c-model-wrapper.component';
import { ModelWrapperComponent } from './projects/models/model-wrapper/model-wrapper.component';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { ProjectWrapperComponent } from './projects/project-wrapper/project-wrapper.component';
import { ActiveSessionsComponent } from './sessions/active-sessions/active-sessions.component';
import { SessionOverviewComponent } from './sessions/session-overview/session-overview.component';
import { AlertSettingsComponent } from './settings/core/alert-settings/alert-settings.component';
import { ToolDetailsComponent } from './settings/core/tools-settings/tool-details/tool-details.component';
import { ToolsSettingsComponent } from './settings/core/tools-settings/tools-settings.component';
import { UserSettingsComponent } from './settings/core/user-settings/user-settings.component';
import { EditGitSettingsComponent } from './settings/modelsources/git-settings/edit-git-settings/edit-git-settings.component';
import { GitSettingsComponent } from './settings/modelsources/git-settings/git-settings.component';
import { EditT4CInstanceComponent } from './settings/modelsources/t4c-settings/edit-t4c-instance/edit-t4c-instance.component';
import { T4CSettingsComponent } from './settings/modelsources/t4c-settings/t4c-settings.component';
import { SettingsComponent } from './settings/settings.component';
import { HomeComponent } from './workspaces/home.component';

const routes: Routes = [
  {
    path: '',
    canActivate: [AuthGuardService],
    children: [
      {
        path: '',
        component: HomeComponent,
      },
      {
        path: 'projects',
        children: [
          {
            path: '',
            component: ProjectOverviewComponent,
          },
          {
            path: 'create',
            component: CreateProjectComponent,
          },
        ],
      },
      {
        path: 'project/:project',
        component: ProjectWrapperComponent,
        children: [
          {
            path: '',
            component: ProjectDetailsComponent,
          },
          {
            path: 'models/create',
            component: CreateModelComponent,
          },
          {
            path: 'model/:model',
            component: ModelWrapperComponent,
            children: [
              {
                path: '',
                component: ModelDetailComponent,
              },
              {
                path: 'git-model',
                children: [
                  { path: 'create', component: CreateCoworkingMethodComponent },
                  {
                    path: ':git-model',
                    component: CreateCoworkingMethodComponent,
                  },
                ],
              },
              {
                path: 't4c-model',
                children: [
                  {
                    path: 'create',
                    component: AddT4cSourceComponent,
                  },
                  {
                    path: ':t4c_model_id',
                    component: T4cModelWrapperComponent,
                    children: [
                      {
                        path: '',
                        component: AddT4cSourceComponent,
                      },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        path: 'workspaces',
        component: HomeComponent,
      },
      {
        path: 'sessions',
        children: [
          {
            path: 'overview',
            component: SessionOverviewComponent,
          },
          {
            path: 'active',
            component: ActiveSessionsComponent,
          },
        ],
      },
      {
        path: 'settings',
        children: [
          {
            path: '',
            component: SettingsComponent,
          },
          {
            path: 'core',
            children: [
              {
                path: 'users',
                component: UserSettingsComponent,
              },
              {
                path: 'alerts',
                component: AlertSettingsComponent,
              },
              {
                path: 'tools',
                children: [
                  {
                    path: '',
                    component: ToolsSettingsComponent,
                  },
                  {
                    path: 'create',
                    component: ToolDetailsComponent,
                  },
                ],
              },
              { path: 'tool/:toolID', component: ToolDetailsComponent },
            ],
          },
          {
            path: 'modelsources',
            children: [
              {
                path: 'git',
                children: [
                  {
                    path: '',
                    component: GitSettingsComponent,
                  },
                  {
                    path: 'instances/:id',
                    component: EditGitSettingsComponent,
                  },
                ],
              },
              {
                path: 't4c',
                children: [
                  {
                    path: '',
                    component: T4CSettingsComponent,
                  },
                  {
                    path: 'create',
                    component: EditT4CInstanceComponent,
                  },
                  {
                    path: 'instance/:instance',
                    component: EditT4CInstanceComponent,
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
  { path: 'auth', component: AuthComponent },
  { path: 'oauth2/callback', component: AuthRedirectComponent },
  {
    path: 'logout/redirect',
    component: LogoutRedirectComponent,
  },
  {
    path: 'logout',
    component: LogoutComponent,
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
