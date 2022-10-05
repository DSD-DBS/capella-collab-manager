/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ActiveSessionsComponent } from './sessions/active-sessions/active-sessions.component';
import { AuthGuardService } from './general/auth/auth-guard/auth-guard.service';
import { AuthRedirectComponent } from './general/auth/auth-redirect/auth-redirect.component';
import { AuthComponent } from './general/auth/auth/auth.component';
import { LogoutRedirectComponent } from './general/auth/logout/logout-redirect/logout-redirect.component';
import { LogoutComponent } from './general/auth/logout/logout/logout.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { ModelDetailComponent } from './projects/project-detail/model-overview/model-detail/model-detail.component';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { SessionOverviewComponent } from './sessions/session-overview/session-overview.component';
import { AlertSettingsComponent } from './settings/core/alert-settings/alert-settings.component';
import { DockerimageSettingsComponent } from './settings/core/dockerimage-settings/dockerimage-settings.component';
import { UserSettingsComponent } from './settings/core/user-settings/user-settings.component';
import { T4CImporterSettingsComponent } from './settings/integrations/backups/t4c-importer-settings/t4c-importer-settings.component';
import { GuacamoleSettingsComponent } from './settings/integrations/guacamole-settings/guacamole-settings.component';
import { EditGitSettingsComponent } from './settings/modelsources/git-settings/edit-git-settings/edit-git-settings.component';
import { GitSettingsComponent } from './settings/modelsources/git-settings/git-settings.component';
import { T4CInstanceSettingsComponent } from './settings/modelsources/t4c-settings/t4c-instance-settings/t4c-instance-settings.component';
import { T4CSettingsComponent } from './settings/modelsources/t4c-settings/t4c-settings.component';
import { SettingsComponent } from './settings/settings.component';
import { HomeComponent } from './workspaces/home.component';
import { ProjectWrapperComponent } from './projects/project-wrapper/project-wrapper.component';
import { ModelWrapperComponent } from './projects/models/model-wrapper/model-wrapper.component';
import { CreateModelComponent } from './projects/models/create-model/create-model.component';
import { EditT4CInstanceComponent } from './settings/modelsources/t4c-settings/edit-t4c-instance/edit-t4c-instance.component';

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
        canActivate: [AuthGuardService],
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
                path: 'dockerimages',
                component: DockerimageSettingsComponent,
              },
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
          {
            path: 'integrations',
            children: [
              {
                path: 'backups/importer',
                component: T4CImporterSettingsComponent,
              },
              {
                path: 'guacamole',
                component: GuacamoleSettingsComponent,
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
