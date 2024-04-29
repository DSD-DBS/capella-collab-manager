/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { DialogRef } from '@angular/cdk/dialog';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { Model } from 'src/app/projects/models/service/model.service';
import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import {
  Tool,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';
import { CreateReadonlySessionDialogComponent } from './create-readonly-session-dialog.component';

class MockSessionService implements Partial<SessionService> {}

const meta: Meta<CreateReadonlySessionDialogComponent> = {
  title: 'Session Components / Create Readonly Session Dialog',
  component: CreateReadonlySessionDialogComponent,
};

const primaryGitModel: GetGitModel = {
  id: 1,
  primary: true,
  path: 'fakePath',
  revision: 'fakeRevision',
  entrypoint: 'fakeEntrypoint',
  password: false,
  username: 'fakeUsername',
};

const version: ToolVersion = {
  id: 1,
  name: 'fakeVersion',
  config: {
    is_recommended: true,
    is_deprecated: false,
    compatible_versions: [],
  },
};

const tool: Tool = {
  id: 1,
  name: 'fakeTool',
  integrations: { t4c: true, pure_variants: null, jupyter: null },
  config: {
    connection: {
      methods: [
        {
          id: '1',
          name: 'fakeConnectionMethod',
          description: 'fakeConnectionMethodDescription',
          type: 'http' as const,
        },
      ],
    },
    provisioning: { max_number_of_models: 1 },
  },
};

const data = {
  tool: tool,
  toolVersion: version,
  models: [],
  projectSlug: '',
};

function createModelWithId(id: number): Model {
  return {
    id: 1,
    name: `fakeModelName-${id}`,
    slug: `fakeModelSlug-${id}`,
    project_slug: 'fakeProjectSlug',
    description: `fakeModelDescription-${id}`,
    tool: tool,
    version: version,
    t4c_models: [],
    git_models: [primaryGitModel],
    restrictions: { allow_pure_variants: false },
    display_order: 1,
  };
}

export default meta;
type Story = StoryObj<CreateReadonlySessionDialogComponent>;

export const ModelSelectedAndStartSessionPossible: Story = {
  args: {
    modelOptions: [
      {
        model: createModelWithId(1),
        primaryGitModel: primaryGitModel,
        revision: primaryGitModel.revision,
        include: true,
        deepClone: false,
      },
    ],
    data: data,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: SessionService,
          useFactory: () => new MockSessionService(),
        },
        { provide: MAT_DIALOG_DATA, useValue: {} },
        { provide: DialogRef, useValue: {} },
      ],
    }),
  ],
};

export const NoModelsToShow: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: SessionService,
          useFactory: () => new MockSessionService(),
        },
        { provide: MAT_DIALOG_DATA, useValue: {} },
        { provide: DialogRef, useValue: {} },
      ],
    }),
  ],
};

export const MaxNumberOfModelsExceeded: Story = {
  args: {
    maxNumberOfModels: 1,
    modelOptions: [
      {
        model: createModelWithId(1),
        primaryGitModel: primaryGitModel,
        revision: primaryGitModel.revision,
        include: true,
        deepClone: false,
      },
      {
        model: createModelWithId(2),
        primaryGitModel: primaryGitModel,
        revision: primaryGitModel.revision,
        include: true,
        deepClone: false,
      },
    ],
    data: data,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: SessionService,
          useFactory: () => new MockSessionService(),
        },
        { provide: MAT_DIALOG_DATA, useValue: {} },
        { provide: DialogRef, useValue: {} },
      ],
    }),
  ],
};

export const ShowNoteForCompatibleSession: Story = {
  args: {
    modelOptions: [
      {
        model: createModelWithId(1),
        primaryGitModel: primaryGitModel,
        revision: primaryGitModel.revision,
        include: true,
        deepClone: false,
      },
    ],
    data: {
      tool: { ...tool, id: 2, name: 'compatibleTool' },
      toolVersion: { ...version, id: 2, name: 'compatibleVersion' },
      models: [],
      projectSlug: '',
    },
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: SessionService,
          useFactory: () => new MockSessionService(),
        },
        { provide: MAT_DIALOG_DATA, useValue: {} },
        { provide: DialogRef, useValue: {} },
      ],
    }),
  ],
};
