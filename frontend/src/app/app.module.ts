/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ClipboardModule } from '@angular/cdk/clipboard';
import { OverlayModule } from '@angular/cdk/overlay';
import { CommonModule } from '@angular/common';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatRippleModule } from '@angular/material/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSortModule } from '@angular/material/sort';
import { MatStepperModule } from '@angular/material/stepper';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatTreeModule } from '@angular/material/tree';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CookieModule } from 'ngx-cookie';
import { MarkdownModule } from 'ngx-markdown';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { ToastrModule } from 'ngx-toastr';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { EventsComponent } from './events/events.component';
import { AuthComponent } from './general/auth/auth/auth.component';
import { AuthInterceptor } from './general/auth/http-interceptor/auth.interceptor';
import { LogoutRedirectComponent } from './general/auth/logout/logout-redirect/logout-redirect.component';
import { LogoutComponent } from './general/auth/logout/logout/logout.component';
import { ErrorHandlingInterceptor } from './general/error-handling/error-handling.interceptor';
import { FooterComponent } from './general/footer/footer.component';
import { LegalComponent } from './general/footer/legal/legal.component';
import { TermsConditionsComponent } from './general/footer/terms-conditions/terms-conditions.component';
import { ReleaseNotesComponent } from './general/metadata/release-notes/release-notes.component';
import { VersionComponent } from './general/metadata/version/version.component';
import { HeaderComponent } from './general/navbar/header.component';
import { NoticeComponent } from './general/notice/notice.component';
import { MatIconComponent } from './helpers/mat-icon/mat-icon.component';
import { ButtonSkeletonLoaderComponent } from './helpers/skeleton-loaders/button-skeleton-loader/button-skeleton-loader.component';
import { FormFieldSkeletonLoaderComponent } from './helpers/skeleton-loaders/form-field-skeleton-loader/form-field-skeleton-loader.component';
import { MatCardOverviewLoaderComponent } from './helpers/skeleton-loaders/mat-card-overview-loader/mat-card-overview-loader.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { CreateBackupComponent } from './projects/models/backup-settings/create-backup/create-backup.component';
import { TriggerPipelineComponent } from './projects/models/backup-settings/trigger-pipeline/trigger-pipeline.component';
import { ViewLogsDialogComponent } from './projects/models/backup-settings/view-logs-dialog/view-logs-dialog.component';
import { ChooseInitComponent } from './projects/models/choose-init/choose-init.component';
import { CreateModelBaseComponent } from './projects/models/create-model-base/create-model-base.component';
import { CreateModelComponent } from './projects/models/create-model/create-model.component';
import { InitModelComponent } from './projects/models/init-model/init-model.component';
import { ModelDescriptionComponent } from './projects/models/model-description/model-description.component';
import { ModelDetailComponent } from './projects/models/model-detail/model-detail.component';
import { T4cModelWrapperComponent } from './projects/models/model-detail/t4c-model-wrapper/t4c-model-wrapper.component';
import { ChooseSourceComponent } from './projects/models/model-source/choose-source.component';
import { ManageGitModelComponent } from './projects/models/model-source/git/manage-git-model/manage-git-model.component';
import { ManageT4CModelComponent } from './projects/models/model-source/t4c/manage-t4c-model/manage-t4c-model.component';
import { ModelWrapperComponent } from './projects/models/model-wrapper/model-wrapper.component';
import { ModelOverviewComponent } from './projects/project-detail/model-overview/model-overview.component';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { ProjectMetadataComponent } from './projects/project-detail/project-metadata/project-metadata.component';
import { ProjectUserSettingsComponent } from './projects/project-detail/project-users/project-user-settings.component';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { ProjectWrapperComponent } from './projects/project-wrapper/project-wrapper.component';
import { WhitespaceUrlInterceptor } from './services/encoder/encoder.interceptor';
import { ActiveSessionsComponent } from './sessions/active-sessions/active-sessions.component';
import { FileBrowserComponent } from './sessions/active-sessions/file-browser/file-browser.component';
import { FileExistsDialogComponent } from './sessions/active-sessions/file-browser/file-exists-dialog/file-exists-dialog.component';
import { DeleteSessionDialogComponent } from './sessions/delete-session-dialog/delete-session-dialog.component';
import { NewReadonlyModelOptionsComponent } from './sessions/new-readonly-session-dialog/new-readonly-model-options/new-readonly-model-options.component';
import { NewReadonlySessionDialogComponent } from './sessions/new-readonly-session-dialog/new-readonly-session-dialog.component';
import { GuacamoleComponent } from './sessions/session-created/guacamole/guacamole.component';
import { SessionOverviewComponent } from './sessions/session-overview/session-overview.component';
import { AlertSettingsComponent } from './settings/core/alert-settings/alert-settings.component';
import { ToolDeletionDialogComponent } from './settings/core/tools-settings/tool-details/tool-deletion-dialog/tool-deletion-dialog.component';
import { ToolDetailsComponent } from './settings/core/tools-settings/tool-details/tool-details.component';
import { ToolNatureComponent } from './settings/core/tools-settings/tool-details/tool-nature/tool-nature.component';
import { ToolVersionComponent } from './settings/core/tools-settings/tool-details/tool-version/tool-version.component';
import { ToolsSettingsComponent } from './settings/core/tools-settings/tools-settings.component';
import { UserSettingsComponent } from './settings/core/user-settings/user-settings.component';
import { PureVariantsComponent } from './settings/integrations/pure-variants/pure-variants.component';
import { DeleteGitSettingsDialogComponent } from './settings/modelsources/git-settings/delete-git-settings-dialog/delete-git-settings-dialog.component';
import { EditGitSettingsComponent } from './settings/modelsources/git-settings/edit-git-settings/edit-git-settings.component';
import { GitSettingsComponent } from './settings/modelsources/git-settings/git-settings.component';
import { EditT4CInstanceComponent } from './settings/modelsources/t4c-settings/edit-t4c-instance/edit-t4c-instance.component';
import { LicencesComponent } from './settings/modelsources/t4c-settings/licences/licences.component';
import { T4CInstanceSettingsComponent } from './settings/modelsources/t4c-settings/t4c-instance-settings/t4c-instance-settings.component';
import { T4CRepoDeletionDialogComponent } from './settings/modelsources/t4c-settings/t4c-instance-settings/t4c-repo-deletion-dialog/t4c-repo-deletion-dialog.component';
import { T4CSettingsWrapperComponent } from './settings/modelsources/t4c-settings/t4c-settings-wrapper/t4c-settings-wrapper.component';
import { T4CSettingsComponent } from './settings/modelsources/t4c-settings/t4c-settings.component';
import { SettingsComponent } from './settings/settings.component';
import { WorkspaceComponent } from './workspace/workspace.component';
import { HomeComponent } from './workspaces/home.component';

@NgModule({
  declarations: [
    ActiveSessionsComponent,
    AlertSettingsComponent,
    AppComponent,
    AuthComponent,
    ButtonSkeletonLoaderComponent,
    ChooseInitComponent,
    ChooseSourceComponent,
    CreateBackupComponent,
    CreateModelBaseComponent,
    CreateModelComponent,
    CreateProjectComponent,
    DeleteGitSettingsDialogComponent,
    DeleteSessionDialogComponent,
    EditGitSettingsComponent,
    EditT4CInstanceComponent,
    EventsComponent,
    FileBrowserComponent,
    FileExistsDialogComponent,
    FooterComponent,
    FormFieldSkeletonLoaderComponent,
    GitSettingsComponent,
    GuacamoleComponent,
    HeaderComponent,
    HomeComponent,
    InitModelComponent,
    LegalComponent,
    LicencesComponent,
    LogoutComponent,
    LogoutRedirectComponent,
    ManageGitModelComponent,
    ManageT4CModelComponent,
    MatCardOverviewLoaderComponent,
    MatIconComponent,
    ModelDescriptionComponent,
    ModelDetailComponent,
    ModelOverviewComponent,
    ModelWrapperComponent,
    NewReadonlyModelOptionsComponent,
    NewReadonlySessionDialogComponent,
    NoticeComponent,
    ProjectDetailsComponent,
    ProjectMetadataComponent,
    ProjectOverviewComponent,
    ProjectUserSettingsComponent,
    ProjectWrapperComponent,
    PureVariantsComponent,
    ReleaseNotesComponent,
    SessionOverviewComponent,
    SettingsComponent,
    T4CInstanceSettingsComponent,
    T4cModelWrapperComponent,
    T4CRepoDeletionDialogComponent,
    T4CSettingsComponent,
    T4CSettingsWrapperComponent,
    TermsConditionsComponent,
    ToolDeletionDialogComponent,
    ToolDetailsComponent,
    ToolNatureComponent,
    ToolsSettingsComponent,
    ToolVersionComponent,
    TriggerPipelineComponent,
    UserSettingsComponent,
    VersionComponent,
    ViewLogsDialogComponent,
    WorkspaceComponent,
  ],
  imports: [
    AppRoutingModule,
    BrowserAnimationsModule,
    BrowserModule,
    ClipboardModule,
    CommonModule,
    CookieModule.withOptions(),
    FormsModule,
    HttpClientModule,
    MarkdownModule.forRoot(),
    MatAutocompleteModule,
    MatBadgeModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatCheckboxModule,
    MatDialogModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatMenuModule,
    MatPaginatorModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatRippleModule,
    MatSelectModule,
    MatSlideToggleModule,
    MatSortModule,
    MatStepperModule,
    MatTableModule,
    MatTabsModule,
    MatToolbarModule,
    MatTooltipModule,
    MatTreeModule,
    NgxSkeletonLoaderModule.forRoot(),
    OverlayModule,
    ReactiveFormsModule,
    ToastrModule.forRoot({
      positionClass: 'toast-bottom-left',
      timeOut: 10000,
      extendedTimeOut: 2000,
      maxOpened: 5,
      preventDuplicates: true,
      countDuplicates: true,
      resetTimeoutOnDuplicate: true,
      includeTitleDuplicates: true,
    }),
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
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ErrorHandlingInterceptor,
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
