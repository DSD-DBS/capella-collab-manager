/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ActiveSessionsComponent } from './active-sessions/active-sessions.component';
import { AuthGuardService } from './auth/auth-guard/auth-guard.service';
import { AuthRedirectComponent } from './auth/auth-redirect/auth-redirect.component';
import { AuthComponent } from './auth/auth/auth.component';
import { LogoutRedirectComponent } from './auth/logout/logout-redirect/logout-redirect.component';
import { LogoutComponent } from './auth/logout/logout/logout.component';
import { MaintenanceComponent } from './maintenance/maintenance.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { ModelDetailComponent } from './projects/project-detail/model-overview/model-detail/model-detail.component';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { SessionOverviewComponent } from './session-overview/session-overview.component';
import { AlertSettingsComponent } from './settings/core/alert-settings/alert-settings.component';
import { DockerimageSettingsComponent } from './settings/core/dockerimage-settings/dockerimage-settings.component';
import { UserSettingsComponent } from './settings/core/user-settings/user-settings.component';
import { T4CImporterSettingsComponent } from './settings/integrations/backups/t4c-importer-settings/t4c-importer-settings.component';
import { GuacamoleSettingsComponent } from './settings/integrations/guacamole-settings/guacamole-settings.component';
import { EditGitSettingsComponent } from './settings/modelsources/git-settings/edit-git-settings/edit-git-settings.component';
import { GitSettingsComponent } from './settings/modelsources/git-settings/git-settings.component';
import { T4CInstanceSettingsComponent } from './settings/modelsources/t4c-settings/t4c-instance-settings/t4c-instance-settings.component';
import { T4CSettingsComponent } from './settings/modelsources/t4c-settings/t4c-settings.component';
import { RequestsComponent } from './settings/requests/requests.component';
import { SettingsComponent } from './settings/settings.component';
import { HomeComponent } from './workspaces/home.component';
import { CreateModelComponent } from './models/create-model/create-model.component';
import { CreateCoworkingMethodComponent } from './models/create-coworking-method/create-coworking-method.component';
import { ChooseSourceComponent } from './models/choose-source/choose-source.component';
import { InitModelComponent } from './models/init-model/init-model.component';
import { ChooseInitComponent } from './models/choose-init/choose-init.component';
import { ProjectWrapperComponent } from './projects/project-wrapper/project-wrapper.component';
import { ModelWrapperComponent } from './models/model-wrapper/model-wrapper.component';

const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'projects',
    component: ProjectOverviewComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'workspaces',
    component: HomeComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'maintenance',
    component: MaintenanceComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'active-sessions',
    component: ActiveSessionsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'overview',
    component: SessionOverviewComponent,
    canActivate: [AuthGuardService],
  },
  { path: 'auth', component: AuthComponent },
  { path: 'oauth2/callback', component: AuthRedirectComponent },
  {
    path: 'settings',
    component: SettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/requests',
    component: RequestsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/core/users',
    component: UserSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/core/alerts',
    component: AlertSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/core/dockerimages',
    component: DockerimageSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/modelsources/git',
    component: GitSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/modelsources/git/edit/:id',
    component: EditGitSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/modelsources/t4c',
    component: T4CSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/modelsources/t4c/instances/:id',
    component: T4CInstanceSettingsComponent,
    canActivate: [AuthGuardService],
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
          {
            path: 'choose-source',
            component: ChooseSourceComponent,
          },
          {
            path: 'choose-init',
            component: ChooseInitComponent,
          },
          {
            path: 'use-existing-git',
            component: CreateCoworkingMethodComponent,
          },
          {
            path: 'init-model',
            component: InitModelComponent,
          },
        ],
      },
    ],
  },
  {
    path: 'settings/integrations/backups/importer',
    component: T4CImporterSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/integrations/guacamole',
    component: GuacamoleSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'create-project',
    component: CreateProjectComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/modelsources/git/instances/:id',
    component: EditGitSettingsComponent,
    canActivate: [AuthGuardService],
  },
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
