/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { Data, RouterModule, Routes } from '@angular/router';
import { JobRunOverviewComponent } from 'src/app/projects/models/backup-settings/job-run-overview/job-run-overview.component';
import { PipelineRunWrapperComponent } from 'src/app/projects/models/backup-settings/pipeline-runs/wrapper/pipeline-run-wrapper/pipeline-run-wrapper.component';
import { ViewLogsDialogComponent } from 'src/app/projects/models/backup-settings/view-logs-dialog/view-logs-dialog.component';
import { PipelineWrapperComponent } from 'src/app/projects/models/backup-settings/wrapper/pipeline-wrapper/pipeline-wrapper.component';
import { ModelRestrictionsComponent } from 'src/app/projects/models/model-restrictions/model-restrictions.component';
import { EditProjectMetadataComponent } from 'src/app/projects/project-detail/edit-project-metadata/edit-project-metadata.component';
import { SessionComponent } from 'src/app/sessions/session/session.component';
import { PipelinesOverviewComponent } from 'src/app/settings/core/pipelines-overview/pipelines-overview.component';
import { EditPolarionSettingsComponent } from 'src/app/settings/modelsources/polarion-settings/edit-polarion-settings/edit-polarion-settings.component';
import { PolarionSettingsComponent } from 'src/app/settings/modelsources/polarion-settings/polarion-settings.component';
import { BasicAuthTokenComponent } from 'src/app/users/basic-auth-token/basic-auth-token.component';
import { UsersProfileComponent } from 'src/app/users/users-profile/users-profile.component';
import { EventsComponent } from './events/events.component';
import { AuthComponent } from './general/auth/auth/auth.component';
import { AuthGuardService } from './general/auth/auth-guard/auth-guard.service';
import { AuthRedirectComponent } from './general/auth/auth-redirect/auth-redirect.component';
import { LogoutComponent } from './general/auth/logout/logout/logout.component';
import { LogoutRedirectComponent } from './general/auth/logout/logout-redirect/logout-redirect.component';
import { CreateProjectComponent } from './projects/create-project/create-project.component';
import { CreateModelComponent } from './projects/models/create-model/create-model.component';
import { ModelDescriptionComponent } from './projects/models/model-description/model-description.component';
import { ModelDetailComponent } from './projects/models/model-detail/model-detail.component';
import { T4CModelWrapperComponent } from './projects/models/model-detail/t4c-model-wrapper/t4c-model-wrapper.component';
import { ManageGitModelComponent } from './projects/models/model-source/git/manage-git-model/manage-git-model.component';
import { CreateT4cModelNewRepositoryComponent } from './projects/models/model-source/t4c/create-t4c-model-new-repository/create-t4c-model-new-repository.component';
import { ManageT4CModelComponent } from './projects/models/model-source/t4c/manage-t4c-model/manage-t4c-model.component';
import { ModelWrapperComponent } from './projects/models/model-wrapper/model-wrapper.component';
import { ProjectDetailsComponent } from './projects/project-detail/project-details.component';
import { ProjectOverviewComponent } from './projects/project-overview/project-overview.component';
import { ProjectWrapperComponent } from './projects/project-wrapper/project-wrapper.component';
import { SessionOverviewComponent } from './sessions/session-overview/session-overview.component';
import { SessionsComponent } from './sessions/sessions.component';
import { AlertSettingsComponent } from './settings/core/alert-settings/alert-settings.component';
import { ToolDetailsComponent } from './settings/core/tools-settings/tool-details/tool-details.component';
import { ToolsSettingsComponent } from './settings/core/tools-settings/tools-settings.component';
import { UserSettingsComponent } from './settings/core/user-settings/user-settings.component';
import { PureVariantsComponent } from './settings/integrations/pure-variants/pure-variants.component';
import { EditGitSettingsComponent } from './settings/modelsources/git-settings/edit-git-settings/edit-git-settings.component';
import { GitSettingsComponent } from './settings/modelsources/git-settings/git-settings.component';
import { EditT4CInstanceComponent } from './settings/modelsources/t4c-settings/edit-t4c-instance/edit-t4c-instance.component';
import { T4CSettingsWrapperComponent } from './settings/modelsources/t4c-settings/t4c-settings-wrapper/t4c-settings-wrapper.component';
import { T4CSettingsComponent } from './settings/modelsources/t4c-settings/t4c-settings.component';
import { SettingsComponent } from './settings/settings.component';

const routes: Routes = [
  {
    path: '',
    canActivate: [AuthGuardService],
    children: [
      {
        path: '',
        component: SessionsComponent,
        data: { breadcrumb: 'Sessions' },
      },
      {
        path: 'session',
        component: SessionComponent,
        data: { breadcrumb: 'Session Viewer' },
      },
      {
        path: 'projects',
        data: { breadcrumb: 'Projects' },
        children: [
          {
            path: '',
            data: { breadcrumb: undefined },
            component: ProjectOverviewComponent,
          },
          {
            path: 'create',
            data: { breadcrumb: 'Create Project' },
            component: CreateProjectComponent,
          },
        ],
      },
      {
        path: 'project',
        data: { breadcrumb: 'Projects', redirect: '/projects' },
        children: [
          {
            path: ':project',
            data: {
              breadcrumb: (data: Data) => data.project?.name,
              redirect: (data: Data) => `/project/${data.project?.slug}`,
            },
            component: ProjectWrapperComponent,
            children: [
              {
                path: '',
                data: { breadcrumb: undefined },
                component: ProjectDetailsComponent,
              },
              {
                path: 'metadata',
                data: {
                  breadcrumb: 'Configure Project',
                  redirect: (data: Data) =>
                    `/project/${data.project?.slug}/metadata`,
                },
                component: EditProjectMetadataComponent,
              },
              {
                path: 'models',
                children: [
                  {
                    path: 'create',
                    data: { breadcrumb: 'Create Model' },
                    component: CreateModelComponent,
                  },
                ],
              },
              {
                path: 'model',
                children: [
                  {
                    path: ':model',
                    data: {
                      breadcrumb: (data: Data) => data.model?.slug,
                      redirect: (data: Data) =>
                        `/project/${data.project?.slug}`,
                    },
                    component: ModelWrapperComponent,
                    children: [
                      {
                        path: '',
                        data: {
                          breadcrumb: 'Configure Model',
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}/metadata`,
                        },
                        component: ModelDescriptionComponent,
                      },
                      {
                        path: 'modelsources',
                        data: {
                          breadcrumb: 'Model Sources',
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}/modelsources`,
                        },
                        component: ModelDetailComponent,
                      },
                      {
                        path: 'metadata',
                        data: {
                          breadcrumb: 'Configure Model',
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}/metadata`,
                        },
                        component: ModelDescriptionComponent,
                      },
                      {
                        path: 'restrictions',
                        data: {
                          breadcrumb: 'Restrictions',
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}/restrictions`,
                        },
                        component: ModelRestrictionsComponent,
                      },
                      {
                        path: 'pipeline',
                        data: {
                          breadcrumb: 'Pipelines',
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}/pipeline/${data.pipeline?.id}/runs`,
                        },
                        children: [
                          {
                            path: ':pipeline',
                            data: {
                              breadcrumb: (data: Data) => data.pipeline?.id,
                              redirect: (data: Data) =>
                                `/project/${data.project?.slug}/model/${data.model?.slug}/pipeline/${data.pipeline?.id}/runs`,
                            },
                            component: PipelineWrapperComponent,
                            children: [
                              {
                                path: 'runs',
                                data: {
                                  breadcrumb: () => 'runs',
                                },
                                component: JobRunOverviewComponent,
                              },
                              {
                                path: 'run',
                                data: {
                                  breadcrumb: 'runs',
                                  redirect: (data: Data) =>
                                    `/project/${data.project?.slug}/model/${data.model?.slug}/pipeline/${data.pipeline?.id}/runs`,
                                },
                                children: [
                                  {
                                    path: ':pipelineRun',
                                    component: PipelineRunWrapperComponent,
                                    data: {
                                      breadcrumb: (data: Data) =>
                                        data.pipelineRun?.id,
                                      redirect: (data: Data) =>
                                        `/project/${data.project?.slug}/model/${data.model?.slug}/pipeline/${data.pipeline?.id}/run/${data.pipelineRun?.id}/logs`,
                                    },
                                    children: [
                                      {
                                        path: 'logs',
                                        data: { breadcrumb: 'logs' },
                                        component: ViewLogsDialogComponent,
                                      },
                                    ],
                                  },
                                ],
                              },
                            ],
                          },
                        ],
                      },
                      {
                        path: 'git-model',
                        data: {
                          breadcrumb: 'Model Sources',
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}/modelsources`,
                        },
                        children: [
                          {
                            path: 'create',
                            data: {
                              breadcrumb: 'Create Git Model',
                              redirect: (data: Data) =>
                                `/project/${data.project?.slug}/model/${data.model?.slug}/git-model/create`,
                            },
                            component: ManageGitModelComponent,
                          },
                          {
                            path: ':git-model',
                            data: {
                              breadcrumb: (data: Data) =>
                                data.gitModel?.id || '...',
                              redirect: (data: Data) =>
                                data.gitModel?.id
                                  ? `/project/${data.project?.slug}/model/${data.model?.slug}/git-model/${data.gitModel?.id}`
                                  : undefined,
                            },
                            component: ManageGitModelComponent,
                          },
                        ],
                      },
                      {
                        path: 't4c-model',
                        data: {
                          breadcrumb: 'Model Sources',
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}/modelsources`,
                        },
                        children: [
                          {
                            path: 'create-existing',
                            data: {
                              breadcrumb: 'Create T4C Model',
                              redirect: (data: Data) =>
                                `/project/${data.project?.slug}/model/${data.model?.slug}/t4c-model/create-existing`,
                            },
                            component: ManageT4CModelComponent,
                          },
                          {
                            path: 'create-new',
                            data: {
                              breadcrumb: 'Create T4C Model',
                              redirect: (data: Data) =>
                                `/project/${data.project?.slug}/model/${data.model?.slug}/t4c-model/create-new`,
                            },
                            component: CreateT4cModelNewRepositoryComponent,
                          },
                          {
                            path: ':t4c_model_id',
                            data: {
                              breadcrumb: (data: Data) =>
                                data.t4cModel?.id || '...',
                              redirect: (data: Data) =>
                                data.t4cModel?.id
                                  ? `/project/${data.project?.slug}/model/${data.model?.slug}/t4c-model/${data.t4cModel?.id}`
                                  : undefined,
                            },
                            component: T4CModelWrapperComponent,
                            children: [
                              {
                                path: '',
                                component: ManageT4CModelComponent,
                              },
                            ],
                          },
                        ],
                      },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        path: 'sessions',
        children: [
          {
            path: '',
            component: SessionsComponent,
          },
          {
            path: 'overview',
            data: { breadcrumb: 'Session Overview' },
            component: SessionOverviewComponent,
          },
        ],
      },
      {
        path: 'settings',
        data: { breadcrumb: 'Settings' },
        children: [
          {
            path: '',
            data: { breadcrumb: undefined },
            component: SettingsComponent,
          },
          {
            path: 'core',
            data: { breadcrumb: undefined },
            children: [
              {
                path: 'users',
                data: { breadcrumb: 'Users' },
                component: UserSettingsComponent,
              },
              {
                path: 'alerts',
                data: { breadcrumb: 'Alerts' },
                component: AlertSettingsComponent,
              },
              {
                path: 'pipelines',
                data: { breadcrumb: 'Pipelines' },
                component: PipelinesOverviewComponent,
              },
              {
                path: 'tools',
                data: { breadcrumb: 'Tools' },
                children: [
                  {
                    path: '',
                    data: { breadcrumb: undefined },
                    component: ToolsSettingsComponent,
                  },
                  {
                    path: 'create',
                    data: { breadcrumb: 'Create Tool' },
                    component: ToolDetailsComponent,
                  },
                ],
              },
              {
                path: 'tool/:toolID',
                data: { breadcrumb: 'Tools', redirect: '/settings/core/tools' },
                children: [
                  {
                    path: '',
                    data: {
                      breadcrumb: (data: Data) => data.tool?.name || '...',
                      redirect: (data: Data) =>
                        data.tool?.id
                          ? `/settings/core/tools/${data.tool?.id}`
                          : undefined,
                    },
                    component: ToolDetailsComponent,
                  },
                ],
              },
            ],
          },
          {
            path: 'modelsources',
            data: { breadcrumb: undefined },
            children: [
              {
                path: 'git',
                data: { breadcrumb: 'Git Instances' },
                children: [
                  {
                    path: '',
                    data: { breadcrumb: undefined },
                    component: GitSettingsComponent,
                  },
                  {
                    path: 'instances/:id',
                    data: {
                      breadcrumb: (data: Data) => data.gitInstance?.name,
                    },
                    component: EditGitSettingsComponent,
                  },
                ],
              },
              {
                path: 't4c',
                data: { breadcrumb: 'T4C Instances' },
                component: T4CSettingsWrapperComponent,
                children: [
                  {
                    path: '',
                    data: { breadcrumb: undefined },
                    component: T4CSettingsComponent,
                  },
                  {
                    path: 'create',
                    data: { breadcrumb: 'new' },
                    component: EditT4CInstanceComponent,
                  },
                  {
                    path: 'instance/:instance',
                    data: {
                      breadcrumb: (data: Data) => data.t4cInstance?.name,
                    },
                    component: EditT4CInstanceComponent,
                  },
                ],
              },
              {
                path: 'polarion',
                data: { breadcrumb: 'Polarion Instances' },
                children: [
                  {
                    path: '',
                    data: { breadcrumb: undefined },
                    component: PolarionSettingsComponent,
                  },
                  {
                    path: 'instances/:id',
                    data: {
                      breadcrumb: (data: Data) => data.polarionInstance?.name,
                    },
                    component: EditPolarionSettingsComponent,
                  },
                ],
              },
            ],
          },
          {
            path: 'integrations',
            data: { breadcrumb: undefined },
            children: [
              {
                path: 'pure-variants',
                data: { breadcrumb: 'pure::variants' },
                component: PureVariantsComponent,
              },
            ],
          },
        ],
      },
      {
        path: 'events',
        data: { breadcrumb: 'Events' },
        component: EventsComponent,
      },
      {
        path: 'user/:userId',
        data: { breadcrumb: (data: Data) => data?.user?.name || 'User' },
        component: UsersProfileComponent,
      },
      {
        path: 'tokens',
        data: { breadcrumb: 'Tokens' },
        component: BasicAuthTokenComponent,
      },
    ],
  },
  {
    path: 'auth',
    component: AuthComponent,
  },
  { path: 'oauth2/callback', component: AuthRedirectComponent },
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
