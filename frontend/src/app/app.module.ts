/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ClipboardModule } from '@angular/cdk/clipboard';
import { DragDropModule } from '@angular/cdk/drag-drop';

import { OverlayModule } from '@angular/cdk/overlay';
import { CommonModule } from '@angular/common';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatRippleModule } from '@angular/material/core';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyAutocompleteModule as MatAutocompleteModule } from '@angular/material/legacy-autocomplete';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatLegacyCheckboxModule as MatCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { MatLegacyListModule as MatListModule } from '@angular/material/legacy-list';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { MatLegacyPaginatorModule as MatPaginatorModule } from '@angular/material/legacy-paginator';
import { MatLegacyProgressBarModule as MatProgressBarModule } from '@angular/material/legacy-progress-bar';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { MatLegacySlideToggleModule as MatSlideToggleModule } from '@angular/material/legacy-slide-toggle';
import { MatLegacyTableModule as MatTableModule } from '@angular/material/legacy-table';
import { MatLegacyTabsModule as MatTabsModule } from '@angular/material/legacy-tabs';
import { MatLegacyTooltipModule as MatTooltipModule } from '@angular/material/legacy-tooltip';
import { MatRadioModule } from '@angular/material/radio';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatSortModule } from '@angular/material/sort';
import { MatStepperModule } from '@angular/material/stepper';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTreeModule } from '@angular/material/tree';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CookieModule } from 'ngx-cookie';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { ToastrModule } from 'ngx-toastr';
import { BasicAuthTokenComponent } from 'src/app/users/basic-auth-token/basic-auth-token.component';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { EventsComponent } from './events/events.component';
import { AuthComponent } from './general/auth/auth/auth.component';
import { AuthInterceptor } from './general/auth/http-interceptor/auth.interceptor';
import { LogoutComponent } from './general/auth/logout/logout/logout.component';
import { LogoutRedirectComponent } from './general/auth/logout/logout-redirect/logout-redirect.component';
import { BreadcrumbsComponent } from './general/breadcrumbs/breadcrumbs.component';
import { ErrorHandlingInterceptor } from './general/error-handling/error-handling.interceptor';
import { FooterComponent } from './general/footer/footer.component';
import { LegalComponent } from './general/footer/legal/legal.component';
import { HeaderComponent } from './general/header/header.component';
import { VersionComponent } from './general/metadata/version/version.component';
import { NavBarMenuComponent } from './general/nav-bar-menu/nav-bar-menu.component';
import { NoticeComponent } from './general/notice/notice.component';
import { ConfirmationDialogComponent } from './helpers/confirmation-dialog/confirmation-dialog.component';
import { DisplayValueComponent } from './helpers/display-value/display-value.component';
import { InputDialogComponent } from './helpers/input-dialog/input-dialog.component';
import { MatIconComponent } from './helpers/mat-icon/mat-icon.component';
import { ButtonSkeletonLoaderComponent } from './helpers/skeleton-loaders/button-skeleton-loader/button-skeleton-loader.component';
import { FormFieldSkeletonLoaderComponent } from './helpers/skeleton-loaders/form-field-skeleton-loader/form-field-skeleton-loader.component';
import { MatCardOverviewSkeletonLoaderComponent } from './helpers/skeleton-loaders/mat-card-overview-skeleton-loader/mat-card-overview-skeleton-loader.component';
import { MatCheckboxLoaderComponent } from './helpers/skeleton-loaders/mat-checkbox-loader/mat-checkbox-loader.component';
import { MatListSkeletonLoaderComponent } from './helpers/skeleton-loaders/mat-list-skeleton-loader/mat-list-skeleton-loader.component';
import { TextLineSkeletonLoaderComponent } from './helpers/skeleton-loaders/text-line-skeleton-loader/text-line-skeleton-loader.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { CreateBackupComponent } from './projects/models/backup-settings/create-backup/create-backup.component';
import { JobRunOverviewComponent } from './projects/models/backup-settings/job-run-overview/job-run-overview.component';
import { PipelineRunWrapperComponent } from './projects/models/backup-settings/pipeline-runs/wrapper/pipeline-run-wrapper/pipeline-run-wrapper.component';
import { TriggerPipelineComponent } from './projects/models/backup-settings/trigger-pipeline/trigger-pipeline.component';
import { ViewLogsDialogComponent } from './projects/models/backup-settings/view-logs-dialog/view-logs-dialog.component';
import { PipelineWrapperComponent } from './projects/models/backup-settings/wrapper/pipeline-wrapper/pipeline-wrapper.component';
import { ChooseInitComponent } from './projects/models/choose-init/choose-init.component';
import { CreateModelComponent } from './projects/models/create-model/create-model.component';
import { CreateModelBaseComponent } from './projects/models/create-model-base/create-model-base.component';
import { ModelDiagramDialogComponent } from './projects/models/diagrams/model-diagram-dialog/model-diagram-dialog.component';
import { ModelDiagramPreviewDialogComponent } from './projects/models/diagrams/model-diagram-preview-dialog/model-diagram-preview-dialog.component';
import { InitModelComponent } from './projects/models/init-model/init-model.component';
import { ModelDescriptionComponent } from './projects/models/model-description/model-description.component';
import { ModelDetailComponent } from './projects/models/model-detail/model-detail.component';
import { T4CModelWrapperComponent } from './projects/models/model-detail/t4c-model-wrapper/t4c-model-wrapper.component';
import { ModelRestrictionsComponent } from './projects/models/model-restrictions/model-restrictions.component';
import { ChooseSourceComponent } from './projects/models/model-source/choose-source.component';
import { ManageGitModelComponent } from './projects/models/model-source/git/manage-git-model/manage-git-model.component';
import { CreateT4cModelNewRepositoryComponent } from './projects/models/model-source/t4c/create-t4c-model-new-repository/create-t4c-model-new-repository.component';
import { ManageT4CModelComponent } from './projects/models/model-source/t4c/manage-t4c-model/manage-t4c-model.component';
import { ModelWrapperComponent } from './projects/models/model-wrapper/model-wrapper.component';
import { EditProjectMetadataComponent } from './projects/project-detail/edit-project-metadata/edit-project-metadata.component';
import { ModelComplexityBadgeComponent } from './projects/project-detail/model-overview/model-complexity-badge/model-complexity-badge.component';
import { ModelOverviewComponent } from './projects/project-detail/model-overview/model-overview.component';
import { MoveModelComponent } from './projects/project-detail/model-overview/move-model/move-model.component';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { ProjectMetadataComponent } from './projects/project-detail/project-metadata/project-metadata.component';
import { AddUserToProjectDialogComponent } from './projects/project-detail/project-users/add-user-to-project/add-user-to-project.component';
import { ProjectAuditLogComponent } from './projects/project-detail/project-users/project-audit-log/project-audit-log.component';
import { ProjectUserSettingsComponent } from './projects/project-detail/project-users/project-user-settings.component';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { ProjectWrapperComponent } from './projects/project-wrapper/project-wrapper.component';
import { WhitespaceUrlInterceptor } from './services/encoder/encoder.interceptor';
import { DeleteSessionDialogComponent } from './sessions/delete-session-dialog/delete-session-dialog.component';
import { FloatingWindowManagerComponent } from './sessions/session/floating-window-manager/floating-window-manager.component';
import { SessionIFrameComponent } from './sessions/session/session-iframe/session-iframe.component';
import { SessionComponent } from './sessions/session/session.component';
import { TilingWindowManagerComponent } from './sessions/session/tiling-window-manager/tiling-window-manager.component';
import { SessionOverviewComponent } from './sessions/session-overview/session-overview.component';
import { SessionsComponent } from './sessions/sessions.component';
import { ActiveSessionsComponent } from './sessions/user-sessions-wrapper/active-sessions/active-sessions.component';
import { ConnectionDialogComponent } from './sessions/user-sessions-wrapper/active-sessions/connection-dialog/connection-dialog.component';
import { FileBrowserDialogComponent } from './sessions/user-sessions-wrapper/active-sessions/file-browser-dialog/file-browser-dialog.component';
import { FileExistsDialogComponent } from './sessions/user-sessions-wrapper/active-sessions/file-browser-dialog/file-exists-dialog/file-exists-dialog.component';
import { CreateReadonlySessionComponent } from './sessions/user-sessions-wrapper/create-session/create-readonly-session/create-readonly-session.component';
import { CreatePersistentSessionComponent } from './sessions/user-sessions-wrapper/create-sessions/create-persistent-session/create-persistent-session.component';
import { CreateReadonlyModelOptionsComponent } from './sessions/user-sessions-wrapper/create-sessions/create-readonly-session/create-readonly-model-options/create-readonly-model-options.component';
import { CreateReadonlySessionDialogComponent } from './sessions/user-sessions-wrapper/create-sessions/create-readonly-session/create-readonly-session-dialog.component';
import { UserSessionsWrapperComponent } from './sessions/user-sessions-wrapper/user-sessions-wrapper.component';
import { AlertSettingsComponent } from './settings/core/alert-settings/alert-settings.component';
import { PipelinesOverviewComponent } from './settings/core/pipelines-overview/pipelines-overview.component';
import { ToolDeletionDialogComponent } from './settings/core/tools-settings/tool-details/tool-deletion-dialog/tool-deletion-dialog.component';
import { ToolDetailsComponent } from './settings/core/tools-settings/tool-details/tool-details.component';
import { ToolIntegrationsComponent } from './settings/core/tools-settings/tool-details/tool-integrations/tool-integrations.component';
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
import { UsersProfileComponent } from './users/users-profile/users-profile.component';

@NgModule({
  declarations: [
    ActiveSessionsComponent,
    AddUserToProjectDialogComponent,
    AlertSettingsComponent,
    AppComponent,
    AuthComponent,
    BasicAuthTokenComponent,
    BreadcrumbsComponent,
    ButtonSkeletonLoaderComponent,
    ChooseInitComponent,
    ChooseSourceComponent,
    ConfirmationDialogComponent,
    ConnectionDialogComponent,
    CreateBackupComponent,
    CreateModelBaseComponent,
    CreateModelComponent,
    CreatePersistentSessionComponent,
    CreateProjectComponent,
    CreateReadonlyModelOptionsComponent,
    CreateReadonlySessionComponent,
    CreateReadonlySessionDialogComponent,
    CreateT4cModelNewRepositoryComponent,
    DeleteGitSettingsDialogComponent,
    DeleteSessionDialogComponent,
    DisplayValueComponent,
    EditGitSettingsComponent,
    EditProjectMetadataComponent,
    EditT4CInstanceComponent,
    EventsComponent,
    FileBrowserDialogComponent,
    FileExistsDialogComponent,
    FloatingWindowManagerComponent,
    FooterComponent,
    FormFieldSkeletonLoaderComponent,
    GitSettingsComponent,
    HeaderComponent,
    InitModelComponent,
    InputDialogComponent,
    JobRunOverviewComponent,
    LegalComponent,
    LicencesComponent,
    LogoutComponent,
    LogoutRedirectComponent,
    ManageGitModelComponent,
    ManageT4CModelComponent,
    MatCardOverviewSkeletonLoaderComponent,
    MatCheckboxLoaderComponent,
    MatIconComponent,
    MatListSkeletonLoaderComponent,
    ModelComplexityBadgeComponent,
    ModelDescriptionComponent,
    ModelDetailComponent,
    ModelDiagramDialogComponent,
    ModelDiagramPreviewDialogComponent,
    ModelOverviewComponent,
    ModelRestrictionsComponent,
    ModelWrapperComponent,
    MoveModelComponent,
    NavBarMenuComponent,
    NoticeComponent,
    PipelineRunWrapperComponent,
    PipelinesOverviewComponent,
    PipelineWrapperComponent,
    ProjectAuditLogComponent,
    ProjectDetailsComponent,
    ProjectMetadataComponent,
    ProjectOverviewComponent,
    ProjectUserSettingsComponent,
    ProjectWrapperComponent,
    PureVariantsComponent,
    SessionComponent,
    SessionIFrameComponent,
    SessionOverviewComponent,
    SessionsComponent,
    SettingsComponent,
    T4CInstanceSettingsComponent,
    T4CModelWrapperComponent,
    T4CRepoDeletionDialogComponent,
    T4CSettingsComponent,
    T4CSettingsWrapperComponent,
    TextLineSkeletonLoaderComponent,
    TilingWindowManagerComponent,
    ToolDeletionDialogComponent,
    ToolDetailsComponent,
    ToolIntegrationsComponent,
    ToolNatureComponent,
    ToolsSettingsComponent,
    ToolVersionComponent,
    TriggerPipelineComponent,
    UserSessionsWrapperComponent,
    UserSettingsComponent,
    UsersProfileComponent,
    VersionComponent,
    ViewLogsDialogComponent,
  ],
  imports: [
    AppRoutingModule,
    BrowserAnimationsModule,
    BrowserModule,
    ClipboardModule,
    CommonModule,
    CookieModule.withOptions(),
    DragDropModule,
    FormsModule,
    HttpClientModule,
    MatAutocompleteModule,
    MatBadgeModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatDialogModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatMenuModule,
    MatNativeDateModule,
    MatPaginatorModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatRippleModule,
    MatSelectModule,
    MatSidenavModule,
    MatSlideToggleModule,
    MatSortModule,
    MatStepperModule,
    MatTableModule,
    MatTabsModule,
    MatToolbarModule,
    MatTooltipModule,
    NgxSkeletonLoaderModule.forRoot(),
    MatTreeModule,
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
