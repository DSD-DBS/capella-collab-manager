/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { SessionOverviewComponent } from './session-overview/session-overview.component';
import { MatTableModule } from '@angular/material/table';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HomeComponent } from './home/home.component';
import { HeaderComponent } from './header/header.component';
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
import { NoRepositoryComponent } from './home/no-repository/no-repository.component';
import { RequestSessionComponent } from './home/request-session/request-session.component';
import { SettingsComponent } from './settings/settings.component';
import { AdminSettingsComponent } from './settings/admin-settings/admin-settings.component';
import { RepositoryManagerSettingsComponent } from './settings/repository-manager-settings/repository-manager-settings.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { RepositorySettingsComponent } from './settings/repository-manager-settings/repository-settings/repository-settings.component';
import { MatListModule } from '@angular/material/list';
import { ActiveSessionsComponent } from './active-sessions/active-sessions.component';
import { LogoutComponent } from './auth/logout/logout/logout.component';
import { DeleteSessionDialogComponent } from './delete-session-dialog/delete-session-dialog.component';
import { MatDialogModule } from '@angular/material/dialog';
import { UserSettingsComponent } from './settings/user-settings/user-settings.component';
import { NoticeComponent } from './notice/notice.component';
import { MatExpansionModule } from '@angular/material/expansion';
import { ReconnectDialogComponent } from './active-sessions/reconnect-dialog/reconnect-dialog.component';
import { AlertSettingsComponent } from './settings/admin-settings/alert-settings/alert-settings.component';
import { AdminUserSettingsComponent } from './settings/admin-settings/admin-user-settings/admin-user-settings.component';
import { GitModelSettingsComponent } from './settings/repository-manager-settings/repository-settings/model-source/git-model-settings/git-model-settings.component';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { RepositorySyncSettingsComponent } from './settings/admin-settings/repository-sync-settings/repository-sync-settings.component';
import { T4CRepoSettingsComponent } from './settings/repository-manager-settings/repository-settings/model-source/t4c-repo-settings/t4c-repo-settings.component';
import { RepositoryUserSettingsComponent } from './settings/repository-manager-settings/repository-settings/repository-user-settings/repository-user-settings.component';
import { ProjectDeletionDialogComponent } from './settings/repository-manager-settings/repository-settings/model-source/t4c-repo-settings/project-deletion-dialog/project-deletion-dialog.component';
import { GitModelDeletionDialogComponent } from './settings/repository-manager-settings/repository-settings/model-source/git-model-settings/git-model-deletion-dialog/git-model-deletion-dialog.component';
import { OverlayModule } from '@angular/cdk/overlay';
import { WarningComponent } from './home/request-session/warning/warning.component';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { WhitespaceUrlInterceptor } from './services/encoder/encoder.interceptor';
import { MatMenuModule } from '@angular/material/menu';
import { WorkspaceComponent } from './workspace/workspace.component';
import { FooterComponent } from './footer/footer.component';
import { TermsConditionsComponent } from './footer/terms-conditions/terms-conditions.component';
import { LegalComponent } from './footer/legal/legal.component';
import { LogoutRedirectComponent } from './auth/logout/logout-redirect/logout-redirect.component';
import { CreateRepositoryComponent } from './settings/admin-settings/create-repository/create-repository.component';
import { SessionCreationProgressComponent } from './session-creation-progress/session-creation-progress.component';
import { SessionProgressIconComponent } from './session-creation-progress/session-progress-icon/session-progress-icon.component';
import { LicencesComponent } from './session-overview/licences/licences.component';
import { BackupSettingsComponent } from './settings/repository-manager-settings/repository-settings/backup-settings/backup-settings.component';
import { GitBackupSettingsComponent } from './settings/repository-manager-settings/repository-settings/backup-settings/ease-backup-settings/ease-backup-settings.component';
import { JenkinsBackupSettingsComponent } from './settings/repository-manager-settings/repository-settings/backup-settings/jenkins-backup-settings/jenkins-backup-settings.component';
import { MatTabsModule } from '@angular/material/tabs';
import { CreateEASEBackupComponent } from './settings/repository-manager-settings/repository-settings/backup-settings/ease-backup-settings/create-ease-backup/create-ease-backup.component';
import { ModelSourceComponent } from './settings/repository-manager-settings/repository-settings/model-source/model-source.component';
import { ViewLogsDialogComponent } from './settings/repository-manager-settings/repository-settings/backup-settings/ease-backup-settings/view-logs-dialog/view-logs-dialog.component';
import { UploadDialogComponent } from './active-sessions/upload-dialog/upload-dialog.component';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTreeModule } from '@angular/material/tree';
import { FileExistsDialogComponent } from './active-sessions/upload-dialog/file-exists-dialog/file-exists-dialog.component';
import { CookieModule } from 'ngx-cookie';
import { ReleaseNotesComponent } from './metadata/release-notes/release-notes.component';
import { MarkdownModule } from 'ngx-markdown';
import { VersionComponent } from './metadata/version/version.component';

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
    AdminSettingsComponent,
    RepositoryManagerSettingsComponent,
    RepositorySettingsComponent,
    ActiveSessionsComponent,
    LogoutComponent,
    DeleteSessionDialogComponent,
    UserSettingsComponent,
    NoticeComponent,
    ReconnectDialogComponent,
    AlertSettingsComponent,
    AdminUserSettingsComponent,
    GitModelSettingsComponent,
    RepositorySyncSettingsComponent,
    T4CRepoSettingsComponent,
    RepositoryUserSettingsComponent,
    ProjectDeletionDialogComponent,
    GitModelDeletionDialogComponent,
    WarningComponent,
    WorkspaceComponent,
    FooterComponent,
    TermsConditionsComponent,
    LegalComponent,
    LogoutRedirectComponent,
    CreateRepositoryComponent,
    SessionCreationProgressComponent,
    SessionProgressIconComponent,
    LicencesComponent,
    BackupSettingsComponent,
    GitBackupSettingsComponent,
    JenkinsBackupSettingsComponent,
    CreateEASEBackupComponent,
    ModelSourceComponent,
    ViewLogsDialogComponent,
    UploadDialogComponent,
    FileExistsDialogComponent,
    ReleaseNotesComponent,
    VersionComponent,
  ],
  imports: [
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
    MatSnackBarModule,
    FormsModule,
    OverlayModule,
    MatSlideToggleModule,
    MatMenuModule,
    MatTabsModule,
    MatProgressBarModule,
    MatTreeModule,
    CookieModule.withOptions(),
    MarkdownModule.forRoot(),
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: WhitespaceUrlInterceptor,
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
