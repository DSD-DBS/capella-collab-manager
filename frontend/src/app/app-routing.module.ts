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
import { SessionOverviewComponent } from './session-overview/session-overview.component';
import { CreateRepositoryComponent } from './settings/admin-settings/create-repository/create-repository.component';
import { RepositorySettingsComponent } from './settings/repository-manager-settings/repository-settings/repository-settings.component';
import { SettingsComponent } from './settings/settings.component';
import { DeleteRepositoryComponent } from './settings/repository-manager-settings/repository-settings/delete-repository/delete-repository.component';

const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
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
    path: 'settings/projects/create',
    component: CreateRepositoryComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/projects/:repository/delete',
    component: DeleteRepositoryComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'settings/projects/:repository',
    component: RepositorySettingsComponent,
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
