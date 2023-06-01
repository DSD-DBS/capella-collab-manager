/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { Data, RouterModule, Routes } from '@angular/router';
import { ModelRestrictionsComponent } from 'src/app/projects/models/model-restrictions/model-restrictions.component';
import { EditProjectMetadataComponent } from 'src/app/projects/project-detail/edit-project-metadata/edit-project-metadata.component';
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
import { T4cModelWrapperComponent } from './projects/models/model-detail/t4c-model-wrapper/t4c-model-wrapper.component';
import { ManageGitModelComponent } from './projects/models/model-source/git/manage-git-model/manage-git-model.component';
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
            data: { breadcrumb: 'New Project' },
            component: CreateProjectComponent,
          },
        ],
      },
      {
        path: 'project',
        data: { breadcrumb: 'projects', redirect: '/projects' },
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
                data: {
                  breadcrumb: 'overview',
                  redirect: (data: Data) => `/project/${data.project?.slug}`,
                },
                component: ProjectDetailsComponent,
              },
              {
                path: 'metadata',
                data: {
                  breadcrumb: 'metadata',
                  redirect: (data: Data) =>
                    `/project/${data.project?.slug}/metadata`,
                },
                component: EditProjectMetadataComponent,
              },
              {
                path: 'models/create',
                data: { breadcrumb: 'new model' },
                component: CreateModelComponent,
              },
              {
                path: 'model',
                data: {
                  breadcrumb: 'models',
                  redirect: (data: Data) => `/project/${data.project?.slug}`,
                },

                children: [
                  {
                    path: ':model',
                    component: ModelWrapperComponent,
                    data: {
                      breadcrumb: (data: Data) => data.model?.name,
                      redirect: (data: Data) =>
                        `/project/${data.project?.slug}`,
                    },

                    children: [
                      {
                        path: '',
                        data: {
                          breadcrumb: (data: Data) => data.model?.name || '...',
                        },
                        component: ModelDetailComponent,
                      },
                      {
                        path: 'metadata',
                        data: { breadcrumb: 'metadata' },
                        component: ModelDescriptionComponent,
                      },
                      {
                        path: 'restrictions',
                        data: { breadcrumb: 'restrictions' },
                        component: ModelRestrictionsComponent,
                      },
                      {
                        path: 'git-model',
                        data: {
                          breadcrumb: (data: Data) => data.model?.name || '...',
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}`,
                        },
                        children: [
                          {
                            path: 'create',
                            data: { breadcrumb: 'New Git Model' },
                            component: ManageGitModelComponent,
                          },
                          {
                            path: ':git-model',
                            data: {
                              breadcrumb: (data: Data) =>
                                `Git integration ${data.gitModel?.id || '...'}`,
                            },
                            component: ManageGitModelComponent,
                          },
                        ],
                      },
                      {
                        path: 't4c-model',
                        data: {
                          breadcrumb: (data: Data) => data.model?.name,
                          redirect: (data: Data) =>
                            `/project/${data.project?.slug}/model/${data.model?.slug}`,
                        },
                        children: [
                          {
                            path: 'create',
                            data: { breadcrumb: 'New T4C Model' },
                            component: ManageT4CModelComponent,
                          },
                          {
                            path: ':t4c_model_id',
                            data: {
                              breadcrumb: (data: Data) =>
                                `T4C integration ${data.t4cModel?.id || '...'}`,
                            },
                            component: T4cModelWrapperComponent,
                            children: [
                              {
                                path: '',
                                data: {
                                  breadcrumb: () => 'edit',
                                },
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
        data: { breadcrumb: 'Sessions' },
        children: [
          {
            path: '',
            component: SessionsComponent,
          },
          {
            path: 'overview',
            data: { breadcrumb: 'Overview' },
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
                    data: { breadcrumb: 'New' },
                    component: ToolDetailsComponent,
                  },
                ],
              },
              {
                path: 'tool/:toolID',
                data: { breadcrumb: 'Tool', redirect: '/settings/core/tools' },
                children: [
                  {
                    path: '',
                    data: { breadcrumb: (data: Data) => data.tool?.name },
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
                data: { breadcrumb: 'Git' },
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
                data: { breadcrumb: 'T4C' },
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
