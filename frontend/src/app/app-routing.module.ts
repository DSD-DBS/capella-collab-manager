/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgModule } from '@angular/core';
import { Data, RouterModule, Routes } from '@angular/router';
import EditorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
import { configureMonacoYaml } from 'monaco-yaml';
import { MonacoEditorModule } from 'ngx-monaco-editor-v2';
import { PageNotFoundComponent } from 'src/app/general/404/404.component';
import { authGuard } from 'src/app/general/auth/auth-guard/auth-guard.service';
import { JobRunOverviewComponent } from 'src/app/projects/models/backup-settings/job-run-overview/job-run-overview.component';
import { PipelineRunWrapperComponent } from 'src/app/projects/models/backup-settings/pipeline-runs/wrapper/pipeline-run-wrapper/pipeline-run-wrapper.component';
import { ViewLogsDialogComponent } from 'src/app/projects/models/backup-settings/view-logs-dialog/view-logs-dialog.component';
import { PipelineWrapperComponent } from 'src/app/projects/models/backup-settings/wrapper/pipeline-wrapper/pipeline-wrapper.component';
import { ModelRestrictionsComponent } from 'src/app/projects/models/model-restrictions/model-restrictions.component';
import { CreateProjectToolsComponent } from 'src/app/projects/project-detail/create-project-tools/create-project-tools.component';
import { EditProjectMetadataComponent } from 'src/app/projects/project-detail/edit-project-metadata/edit-project-metadata.component';
import { SessionViewerComponent } from 'src/app/sessions/session/session-viewer.component';
import { ConfigurationSettingsComponent } from 'src/app/settings/core/configuration-settings/configuration-settings.component';
import { TagsComponent } from 'src/app/settings/core/tags/tags.component';
import { CreateToolComponent } from 'src/app/settings/core/tools-settings/create-tool/create-tool.component';
import { AddGitInstanceComponent } from 'src/app/settings/modelsources/git-instances/add-git-instance/add-git-instance.component';
import { PersonalAccessTokensComponent } from 'src/app/users/personal-access-tokens/personal-access-tokens.component';
import { UserWrapperComponent } from 'src/app/users/user-wrapper/user-wrapper.component';
import { UsersProfileComponent } from 'src/app/users/users-profile/users-profile.component';
import { API_DOCS_URL } from './environment';
import { EventsComponent } from './events/events.component';
import { AuthRedirectComponent } from './general/auth/auth-redirect/auth-redirect.component';
import { AuthComponent } from './general/auth/auth/auth.component';
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
import { AnnouncementSettingsComponent } from './settings/core/announcement-settings/announcement-settings.component';
import { ToolDetailsComponent } from './settings/core/tools-settings/tool-details/tool-details.component';
import { ToolsSettingsComponent } from './settings/core/tools-settings/tools-settings.component';
import { PureVariantsComponent } from './settings/integrations/pure-variants/pure-variants.component';
import { EditGitInstanceComponent } from './settings/modelsources/git-instances/edit-git-instance/edit-git-instance.component';
import { GitInstancesComponent } from './settings/modelsources/git-instances/git-instances.component';
import { EditT4CInstanceComponent } from './settings/modelsources/t4c-settings/edit-t4c-instance/edit-t4c-instance.component';
import { EditT4cLicenseServerComponent } from './settings/modelsources/t4c-settings/edit-t4c-license-server/edit-t4c-license-server.component';
import { T4CSettingsWrapperComponent } from './settings/modelsources/t4c-settings/t4c-settings-wrapper/t4c-settings-wrapper.component';
import { T4CSettingsComponent } from './settings/modelsources/t4c-settings/t4c-settings.component';
import { SettingsComponent } from './settings/settings.component';
import { AllPersonalAccessTokensComponent } from './users/personal-access-tokens/all-personal-access-tokens/all-personal-access-tokens.component';
import { UserSettingsComponent } from './users/user-settings/user-settings.component';
import YamlWorker from './yaml.worker.js?worker';

export const routes: Routes = [
  {
    path: '',
    canActivate: [authGuard],
    children: [
      {
        path: '',
        component: SessionsComponent,
        data: { breadcrumb: 'Sessions' },
      },
      {
        path: 'session-viewer',
        component: SessionViewerComponent,
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
                path: 'tools',
                children: [
                  {
                    path: 'link',
                    data: { breadcrumb: 'Link Tool' },
                    component: CreateProjectToolsComponent,
                  },
                ],
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
                        children: [
                          {
                            path: '',
                            data: {
                              breadcrumb: undefined,
                            },
                            component: ModelDetailComponent,
                          },
                          {
                            path: 'git-model',
                            data: {
                              breadcrumb: 'Git Repositories',
                            },
                            children: [
                              {
                                path: 'create',
                                data: {
                                  breadcrumb: 'Add',
                                  redirect: (data: Data) =>
                                    `/project/${data.project?.slug}/model/${data.model?.slug}/modelsources/git-model/create`,
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
                                      ? `/project/${data.project?.slug}/model/${data.model?.slug}/modelsources/git-model/${data.gitModel?.id}`
                                      : undefined,
                                },
                                component: ManageGitModelComponent,
                              },
                            ],
                          },
                          {
                            path: 't4c-model',
                            data: {
                              breadcrumb: 'T4C Repositories',
                            },
                            children: [
                              {
                                path: 'create-existing',
                                data: {
                                  breadcrumb: 'Link Existing Repository',
                                  redirect: (data: Data) =>
                                    `/project/${data.project?.slug}/model/${data.model?.slug}/modelsources/t4c-model/create-existing`,
                                },
                                component: ManageT4CModelComponent,
                              },
                              {
                                path: 'create-new',
                                data: {
                                  breadcrumb: 'Create New Repository',
                                  redirect: (data: Data) =>
                                    `/project/${data.project?.slug}/model/${data.model?.slug}/modelsources/t4c-model/create-new`,
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
                                      ? `/project/${data.project?.slug}/model/${data.model?.slug}/modelsources/t4c-model/${data.t4cModel?.id}`
                                      : undefined,
                                },
                                component: T4CModelWrapperComponent,
                                children: [
                                  {
                                    path: '',
                                    data: {
                                      breadcrumb: undefined,
                                    },
                                    component: ManageT4CModelComponent,
                                  },
                                ],
                              },
                            ],
                          },
                        ],
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
                path: 'tokens',
                data: { breadcrumb: 'Tokens' },
                component: AllPersonalAccessTokensComponent,
              },
              {
                path: 'announcements',
                data: { breadcrumb: 'Announcements' },
                component: AnnouncementSettingsComponent,
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
                    component: CreateToolComponent,
                  },
                ],
              },
              {
                path: 'tool/:toolID',
                data: {
                  breadcrumb: 'Tools',
                  redirect: '/settings/core/tools',
                },
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
              {
                path: 'configuration',
                data: { breadcrumb: 'Configuration' },
                component: ConfigurationSettingsComponent,
              },
              {
                path: 'tags',
                data: { breadcrumb: 'Tags' },
                component: TagsComponent,
              },
            ],
          },
          {
            path: 'modelsources',
            data: { breadcrumb: undefined },
            children: [
              {
                path: 'git-instances',
                data: { breadcrumb: 'Git Instances' },
                children: [
                  {
                    path: '',
                    data: { breadcrumb: undefined },
                    children: [{ path: '', component: GitInstancesComponent }],
                  },
                  {
                    path: 'create',
                    data: { breadcrumb: 'new' },
                    component: AddGitInstanceComponent,
                  },
                ],
              },
              {
                path: 'git-instance',
                data: {
                  breadcrumb: 'Git Instances',
                  redirect: '/settings/modelsources/git-instances',
                },
                children: [
                  {
                    path: ':id',
                    data: {
                      breadcrumb: (data: Data) => data.gitInstance?.name,
                    },
                    component: EditGitInstanceComponent,
                  },
                ],
              },
              {
                path: 't4c',
                data: { breadcrumb: 'T4C' },
                component: T4CSettingsWrapperComponent,
                children: [
                  {
                    path: '',
                    data: { breadcrumb: undefined },
                    component: T4CSettingsComponent,
                  },
                  {
                    path: 'create-instance',
                    data: { breadcrumb: 'New Instance' },
                    component: EditT4CInstanceComponent,
                  },
                  {
                    path: 'instance',
                    data: {
                      breadcrumb: 'Instances',
                      redirect: '/settings/modelsources/t4c',
                    },
                    children: [
                      {
                        path: ':instance',
                        data: {
                          breadcrumb: (data: Data) => data.t4cInstance?.name,
                        },
                        component: EditT4CInstanceComponent,
                      },
                    ],
                  },
                  {
                    path: 'create-license-server',
                    data: { breadcrumb: 'New License Server' },
                    component: EditT4cLicenseServerComponent,
                  },
                  {
                    path: 'license-server',
                    data: {
                      breadcrumb: 'License Servers',
                      redirect: '/settings/modelsources/t4c',
                    },
                    children: [
                      {
                        path: ':licenseServer',
                        data: {
                          breadcrumb: (data: Data) => data.licenseServer?.name,
                        },
                        component: EditT4cLicenseServerComponent,
                      },
                    ],
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
        path: 'users',
        data: { breadcrumb: 'Users' },
        component: UserSettingsComponent,
      },
      {
        path: 'user',
        data: { breadcrumb: 'Users', redirect: '/users' },
        children: [
          {
            path: ':user',
            data: {
              breadcrumb: (data: Data) => data.user?.name,
              redirect: (data: Data) => `/user/${data.user?.id}`,
            },
            component: UserWrapperComponent,
            children: [
              {
                path: '',
                data: { breadcrumb: undefined },
                component: UsersProfileComponent,
              },
            ],
          },
        ],
      },
      {
        path: 'tokens',
        data: { breadcrumb: 'Tokens' },
        component: PersonalAccessTokensComponent,
      },
    ],
  },
  {
    path: 'auth',
    component: AuthComponent,
  },
  { path: 'oauth2/callback', component: AuthRedirectComponent },
  {
    path: 'logout',
    component: AuthComponent,
  },
  { path: '**', pathMatch: 'full', component: PageNotFoundComponent },
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes),
    MonacoEditorModule.forRoot({
      onMonacoLoad: () => {
        window.MonacoEnvironment = {
          getWorker(_, label) {
            switch (label) {
              case 'editorWorkerService':
                return new EditorWorker();
              case 'yaml':
                return new YamlWorker();
              default:
                throw new Error(`Unknown label ${label}`);
            }
          },
        };

        const apiDocsUrl = API_DOCS_URL.startsWith('http')
          ? API_DOCS_URL
          : new URL(API_DOCS_URL, window.location.origin).href;

        // eslint-disable-next-line
        // @ts-ignore We have to use ignore here because this error only occurs in some contexts
        configureMonacoYaml(window.monaco, {
          enableSchemaRequest: true,
          schemas: [
            {
              fileMatch: ['*.globalconfig.yaml'],
              uri: `${apiDocsUrl}/openapi.json#/components/schemas/GlobalConfiguration-Input`,
            },
            {
              fileMatch: ['*.tool.yaml'],
              uri: `${apiDocsUrl}/openapi.json#/components/schemas/CreateTool-Input`,
            },
            {
              fileMatch: ['*.toolnature.yaml'],
              uri: `${apiDocsUrl}/openapi.json#/components/schemas/CreateToolNature-Input`,
            },
            {
              fileMatch: ['*.toolversion.yaml'],
              uri: `${apiDocsUrl}/openapi.json#/components/schemas/CreateToolVersion-Input`,
            },
          ],
        });
      },
    }),
  ],
  exports: [RouterModule],
})
export class AppRoutingModule {}
