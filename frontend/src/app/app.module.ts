// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { SessionOverviewComponent } from './session-overview/session-overview.component';
import { MatTableModule } from '@angular/material/table';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HomeComponent } from './workspaces/home.component';
import { HeaderComponent } from './navbar/header.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { SessionCreatedComponent } from './session-created/session-created.component';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ClipboardModule } from '@angular/cdk/clipboard';
import { AuthComponent } from './auth/auth/auth.component';
import { AuthInterceptor } from './auth/http-interceptor/auth.interceptor';
import { GuacamoleComponent } from './session-created/guacamole/guacamole.component';
import { RDPComponent } from './session-created/rdp/rdp.component';
import { NoRepositoryComponent } from './workspaces/no-repository/no-repository.component';
import { RequestSessionComponent } from './workspaces/request-session/request-session.component';
import { SettingsComponent } from './settings/settings.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { MatListModule } from '@angular/material/list';
import { ActiveSessionsComponent } from './active-sessions/active-sessions.component';
import { LogoutComponent } from './auth/logout/logout/logout.component';
import { DeleteSessionDialogComponent } from './delete-session-dialog/delete-session-dialog.component';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { NoticeComponent } from './notice/notice.component';
import { MatExpansionModule } from '@angular/material/expansion';
import { ReconnectDialogComponent } from './active-sessions/reconnect-dialog/reconnect-dialog.component';
import { AlertSettingsComponent } from './settings/core/alert-settings/alert-settings.component';
import { GitModelSettingsComponent } from './projects/project-detail/model-source/git-model-settings/git-model-settings.component';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { T4CRepoSettingsComponent } from './projects/project-detail/model-source/t4c-repo-settings/t4c-repo-settings.component';
import { RepositoryUserSettingsComponent } from './projects/project-detail/project-users/project-user-settings.component';
import { T4CRepoDeletionDialogComponent } from './settings/modelsources/t4c-settings/t4c-instance-settings/t4c-repo-deletion-dialog/t4c-repo-deletion-dialog.component';
import { GitModelDeletionDialogComponent } from './projects/project-detail/model-source/git-model-settings/git-model-deletion-dialog/git-model-deletion-dialog.component';
import { OverlayModule } from '@angular/cdk/overlay';
import { WarningComponent } from './workspaces/request-session/warning/warning.component';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { WhitespaceUrlInterceptor } from './services/encoder/encoder.interceptor';
import { MatMenuModule } from '@angular/material/menu';
import { WorkspaceComponent } from './workspace/workspace.component';
import { FooterComponent } from './footer/footer.component';
import { TermsConditionsComponent } from './footer/terms-conditions/terms-conditions.component';
import { LegalComponent } from './footer/legal/legal.component';
import { LogoutRedirectComponent } from './auth/logout/logout-redirect/logout-redirect.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { SessionCreationProgressComponent } from './session-creation-progress/session-creation-progress.component';
import { SessionProgressIconComponent } from './session-creation-progress/session-progress-icon/session-progress-icon.component';
import { LicencesComponent } from './session-overview/licences/licences.component';
import { BackupSettingsComponent } from './projects/project-detail/backup-settings/backup-settings.component';
import { GitBackupSettingsComponent } from './projects/project-detail/backup-settings/ease-backup-settings/ease-backup-settings.component';
import { JenkinsBackupSettingsComponent } from './projects/project-detail/backup-settings/jenkins-backup-settings/jenkins-backup-settings.component';
import { MatTabsModule } from '@angular/material/tabs';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { MatRippleModule } from '@angular/material/core';
import { MaintenanceComponent } from './maintenance/maintenance.component';
import { MatStepperModule } from '@angular/material/stepper';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { ModelOverviewComponent } from './projects/project-detail/model-overview/model-overview.component';
import { SetT4CPasswordComponent } from './projects/project-detail/model-source/t4c-repo-settings/set-t4c-password/set-t4c-password.component';
import { UserSettingsComponent } from './settings/core/user-settings/user-settings.component';
import { GitSettingsComponent } from './settings/modelsources/git-settings/git-settings.component';
import { T4CSettingsComponent } from './settings/modelsources/t4c-settings/t4c-settings.component';
import { T4CInstanceSettingsComponent } from './settings/modelsources/t4c-settings/t4c-instance-settings/t4c-instance-settings.component';
import { GuacamoleSettingsComponent } from './settings/integrations/guacamole-settings/guacamole-settings.component';
import { T4CImporterSettingsComponent } from './settings/integrations/backups/t4c-importer-settings/t4c-importer-settings.component';
import { ModelDetailComponent } from './projects/project-detail/model-overview/model-detail/model-detail.component';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ProjectMetadataComponent } from './projects/project-detail/project-metadata/project-metadata.component';
import { MatBadgeModule } from '@angular/material/badge';
import { RequestsComponent } from './settings/requests/requests.component';
import { CommonModule } from '@angular/common';
import { ToastrModule } from 'ngx-toastr';
import { DockerimageSettingsComponent } from './settings/core/dockerimage-settings/dockerimage-settings.component';
import { CookieModule } from 'ngx-cookie';
import { ViewLogsDialogComponent } from './projects/project-detail/backup-settings/ease-backup-settings/view-logs-dialog/view-logs-dialog.component';
import { CreateEASEBackupComponent } from './projects/project-detail/backup-settings/ease-backup-settings/create-ease-backup/create-ease-backup.component';
import { DeleteGitSettingsDialogComponent } from './settings/modelsources/git-settings/delete-git-settings-dialog/delete-git-settings-dialog.component';

@NgModule({
  declarations: [
    AppComponent,
    SessionOverviewComponent,
    HomeComponent,
    HeaderComponent,
    SessionCreatedComponent,
    AuthComponent,
    GuacamoleComponent,
    RDPComponent,
    NoRepositoryComponent,
    RequestSessionComponent,
    SettingsComponent,
    ProjectDetailsComponent,
    ActiveSessionsComponent,
    LogoutComponent,
    DeleteSessionDialogComponent,
    NoticeComponent,
    ReconnectDialogComponent,
    AlertSettingsComponent,
    GitModelSettingsComponent,
    T4CRepoSettingsComponent,
    RepositoryUserSettingsComponent,
    T4CRepoDeletionDialogComponent,
    GitModelDeletionDialogComponent,
    WarningComponent,
    WorkspaceComponent,
    FooterComponent,
    TermsConditionsComponent,
    LegalComponent,
    LogoutRedirectComponent,
    CreateProjectComponent,
    SessionCreationProgressComponent,
    SessionProgressIconComponent,
    LicencesComponent,
    BackupSettingsComponent,
    GitBackupSettingsComponent,
    JenkinsBackupSettingsComponent,
    ProjectOverviewComponent,
    MaintenanceComponent,
    ModelOverviewComponent,
    SetT4CPasswordComponent,
    UserSettingsComponent,
    DockerimageSettingsComponent,
    GitSettingsComponent,
    T4CSettingsComponent,
    T4CInstanceSettingsComponent,
    GuacamoleSettingsComponent,
    T4CImporterSettingsComponent,
    ModelDetailComponent,
    ProjectMetadataComponent,
    RequestsComponent,
    ViewLogsDialogComponent,
    CreateEASEBackupComponent,
    DeleteGitSettingsDialogComponent,
  ],
  imports: [
    CommonModule,
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatTableModule,
    HttpClientModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatSelectModule,
    ReactiveFormsModule,
    ClipboardModule,
    MatFormFieldModule,
    MatInputModule,
    MatListModule,
    MatDialogModule,
    MatExpansionModule,
    MatCheckboxModule,
    FormsModule,
    OverlayModule,
    MatSlideToggleModule,
    MatMenuModule,
    MatTabsModule,
    MatRippleModule,
    MatStepperModule,
    MatButtonToggleModule,
    MatTooltipModule,
    MatBadgeModule,
    ToastrModule.forRoot({
      positionClass: 'toast-bottom-left',
      timeOut: 10000,
      extendedTimeOut: 2000,
      maxOpened: 5,
      preventDuplicates: true,
      countDuplicates: true,
    }),
    CookieModule.withOptions(),
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: WhitespaceUrlInterceptor,
      multi: true,
    },
    {
      provide: MatDialogRef,
      useValue: {},
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
