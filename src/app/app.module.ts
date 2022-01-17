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
import { LogoutComponent } from './auth/logout/logout.component';
import { DeleteSessionDialogComponent } from './delete-session-dialog/delete-session-dialog.component';
import { MatDialogModule } from '@angular/material/dialog';
import { UserSettingsComponent } from './settings/user-settings/user-settings.component';
import { NoticeComponent } from './notice/notice.component';
import { MatExpansionModule } from '@angular/material/expansion';
import { ReconnectDialogComponent } from './active-sessions/reconnect-dialog/reconnect-dialog.component';
import { AlertSettingsComponent } from './settings/admin-settings/alert-settings/alert-settings.component';
import { AdminUserSettingsComponent } from './settings/admin-settings/admin-user-settings/admin-user-settings.component';
import { GitModelSettingsComponent } from './settings/repository-manager-settings/repository-settings/git-model-settings/git-model-settings.component';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { RepositorySyncSettingsComponent } from './settings/admin-settings/repository-sync-settings/repository-sync-settings.component';
import { ProjectSettingsComponent } from './settings/repository-manager-settings/repository-settings/project-settings/project-settings.component';
import { RepositoryUserSettingsComponent } from './settings/repository-manager-settings/repository-settings/repository-user-settings/repository-user-settings.component';
import { ProjectDeletionDialogComponent } from './settings/repository-manager-settings/repository-settings/project-settings/project-deletion-dialog/project-deletion-dialog.component';
import { SimplebarAngularModule } from 'simplebar-angular';
import { JenkinsComponent } from './settings/repository-manager-settings/repository-settings/git-model-settings/jenkins/jenkins.component';
import { FeedbackComponent } from './feedback/feedback.component';
import { GitModelDeletionDialogComponent } from './settings/repository-manager-settings/repository-settings/git-model-settings/git-model-deletion-dialog/git-model-deletion-dialog.component';
import { OverlayModule } from '@angular/cdk/overlay';
import { WarningComponent } from './home/request-session/warning/warning.component';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { WhitespaceUrlInterceptor } from './services/encoder/encoder.interceptor';

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
    ProjectSettingsComponent,
    RepositoryUserSettingsComponent,
    ProjectDeletionDialogComponent,
    JenkinsComponent,
    FeedbackComponent,
    GitModelDeletionDialogComponent,
    WarningComponent,
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
    SimplebarAngularModule,
    OverlayModule,
    MatSlideToggleModule,
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
