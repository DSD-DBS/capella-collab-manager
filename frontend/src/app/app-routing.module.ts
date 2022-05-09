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
import { HomeComponent } from './home/home.component';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { SessionOverviewComponent } from './session-overview/session-overview.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { SettingsComponent } from './settings/settings.component';
import { MaintenanceComponent } from './maintenance/maintenance.component';

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
