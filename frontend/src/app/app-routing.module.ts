/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { Data, RouterModule, Routes } from '@angular/router';
import { ModelRestrictionsComponent } from 'src/app/projects/models/model-restrictions/model-restrictions.component';
import { EventsComponent } from './events/events.component';
import { AuthGuardService } from './general/auth/auth-guard/auth-guard.service';
import { AuthRedirectComponent } from './general/auth/auth-redirect/auth-redirect.component';
import { AuthComponent } from './general/auth/auth/auth.component';
import { LogoutRedirectComponent } from './general/auth/logout/logout-redirect/logout-redirect.component';
import { LogoutComponent } from './general/auth/logout/logout/logout.component';
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
import { ActiveSessionsComponent } from './sessions/active-sessions/active-sessions.component';
import { SessionOverviewComponent } from './sessions/session-overview/session-overview.component';
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
import { HomeComponent } from './workspaces/home.component';

const routes: Routes = [
  {
    path: '',
    canActivate: [AuthGuardService],
    children: [
      {
        path: '',
        component: HomeComponent,
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
        path: 'project/:project',
        data: { breadcrumb: 'Projects', redirect: '/projects' },
        component: ProjectWrapperComponent,
        children: [
          {
            path: '',
            data: { breadcrumb: (data: Data) => data.project?.name },
            component: ProjectDetailsComponent,
          },
          {
            path: 'models/create',
            data: { breadcrumb: 'New Model' },
            component: CreateModelComponent,
          },
          {
            path: 'model/:model',
            data: {
              breadcrumb: (data: Data) => data.project?.name,
              redirect: (data: Data) => `/project/${data.project?.slug}`,
            },
            component: ModelWrapperComponent,
            children: [
              {
                path: '',
                data: {
                  breadcrumb: (data: Data) =>
                    `${data.model?.name || '...'} models`,
                },
                component: ModelDetailComponent,
              },
              {
                path: 'metadata',
                data: { breadcrumb: (data: Data) => data.model?.name },
                component: ModelDescriptionComponent,
              },
              {
                path: 'restrictions',
                data: { breadcrumb: (data: Data) => data.model?.name },
                component: ModelRestrictionsComponent,
              },
              {
                path: 'git-model',
                data: {
                  breadcrumb: (data: Data) => data.model?.name,
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
                    data: { breadcrumb: 'Edit Git Model' },
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
                    data: { breadcrumb: 'Edit T4C Model' },
                    component: T4cModelWrapperComponent,
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
      {
        path: 'workspaces',
        data: { breadcrumb: 'Workspaces' },
        component: HomeComponent,
      },
      {
        path: 'sessions',
        data: { breadcrumb: 'Sessions' },
        children: [
          {
            path: 'overview',
            data: { breadcrumb: 'Overview' },
            component: SessionOverviewComponent,
          },
          {
            path: 'active',
            data: { breadcrumb: 'Active' },
            component: ActiveSessionsComponent,
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
                data: { breadcrumb: 'Tool' },
                children: [
                  {
                    path: '',
                    data: { breadcrumb: undefined },
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
                    data: { breadcrumb: 'Edit' },
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
                    data: { breadcrumb: 'New' },
                    component: EditT4CInstanceComponent,
                  },
                  {
                    path: 'instance/:instance',
                    data: { breadcrumb: 'Edit' },
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
                data: { breadcrumb: 'Pure::Variants' },
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
