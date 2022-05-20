// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ActiveSessionsComponent } from './active-sessions/active-sessions.component';
import { AuthGuardService } from './auth/auth-guard/auth-guard.service';
import { AuthRedirectComponent } from './auth/auth-redirect/auth-redirect.component';
import { AuthComponent } from './auth/auth/auth.component';
import { LogoutRedirectComponent } from './auth/logout/logout-redirect/logout-redirect.component';
import { LogoutComponent } from './auth/logout/logout/logout.component';
import { HomeComponent } from './workspaces/home.component';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { SessionOverviewComponent } from './session-overview/session-overview.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { SettingsComponent } from './settings/settings.component';
import { MaintenanceComponent } from './maintenance/maintenance.component';
import { UserSettingsComponent } from './settings/core/user-settings/user-settings.component';
import { AlertSettingsComponent } from './settings/core/alert-settings/alert-settings.component';
import { WorkspaceSettingsComponent } from './settings/core/workspace-settings/workspace-settings.component';
import { GitSettingsComponent } from './settings/modelsources/git-settings/git-settings.component';
import { T4CSettingsComponent } from './settings/modelsources/t4c-settings/t4c-settings.component';
import { T4CInstanceSettingsComponent } from './settings/modelsources/t4c-settings/t4c-instance-settings/t4c-instance-settings.component';
import { T4CImporterSettingsComponent } from './settings/integrations/backups/t4c-importer-settings/t4c-importer-settings.component';
import { GuacamoleSettingsComponent } from './settings/integrations/guacamole-settings/guacamole-settings.component';

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
    path: 'settings/core/workspaces',
    component: WorkspaceSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/core/workspaces',
    component: WorkspaceSettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/modelsources/git',
    component: GitSettingsComponent,
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
    path: 'projects/create',
    component: CreateProjectComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'projects/:project',
    component: ProjectDetailsComponent,
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
