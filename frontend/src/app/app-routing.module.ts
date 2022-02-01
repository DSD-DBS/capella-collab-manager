import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ActiveSessionsComponent } from './active-sessions/active-sessions.component';
import { AuthGuardService } from './auth/auth-guard/auth-guard.service';
import { AuthRedirectComponent } from './auth/auth-redirect/auth-redirect.component';
import { AuthComponent } from './auth/auth/auth.component';
import { LogoutComponent } from './auth/logout/logout.component';
import { FeedbackComponent } from './feedback/feedback.component';
import { HomeComponent } from './home/home.component';
import { SessionOverviewComponent } from './session-overview/session-overview.component';
import { RepositorySettingsComponent } from './settings/repository-manager-settings/repository-settings/repository-settings.component';
import { SettingsComponent } from './settings/settings.component';

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
    path: 'settings/repositories/:repository',
    component: RepositorySettingsComponent,
    canActivate: [AuthGuardService],
  },
  {
    path: 'logout',
    component: LogoutComponent,
  },
  {
    path: 'feedback',
    component: FeedbackComponent,
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
