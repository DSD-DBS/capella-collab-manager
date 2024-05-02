/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { Tool } from 'src/app/openapi';
import { SessionService } from 'src/app/sessions/service/session.service';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockPrimaryGitModel } from 'src/storybook/git';
import { createModelWithId } from 'src/storybook/model';
import { mockTool, mockToolVersion } from 'src/storybook/tool';
import { CreateReadonlySessionDialogComponent } from './create-readonly-session-dialog.component';

class MockSessionService implements Partial<SessionService> {}

const meta: Meta<CreateReadonlySessionDialogComponent> = {
  title: 'Session Components / Create Readonly Session Dialog',
  component: CreateReadonlySessionDialogComponent,
  decorators: [
    moduleMetadata({
      providers: [{ provide: MAT_DIALOG_DATA, useValue: {} }],
    }),
    dialogWrapper,
  ],
};

const tool: Tool = { ...mockTool };
tool.config.provisioning.max_number_of_models = 1;

const data = {
  tool: tool,
  toolVersion: mockToolVersion,
  models: [],
  projectSlug: '',
};

export default meta;
type Story = StoryObj<CreateReadonlySessionDialogComponent>;

export const ModelSelectedAndStartSessionPossible: Story = {
  args: {
    modelOptions: [
      {
        model: createModelWithId(1),
        primaryGitModel: mockPrimaryGitModel,
        revision: mockPrimaryGitModel.revision,
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
        primaryGitModel: mockPrimaryGitModel,
        revision: mockPrimaryGitModel.revision,
        include: true,
        deepClone: false,
      },
      {
        model: createModelWithId(2),
        primaryGitModel: mockPrimaryGitModel,
        revision: mockPrimaryGitModel.revision,
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
      ],
    }),
  ],
};

export const ShowNoteForCompatibleSession: Story = {
  args: {
    modelOptions: [
      {
        model: createModelWithId(1),
        primaryGitModel: mockPrimaryGitModel,
        revision: mockPrimaryGitModel.revision,
        include: true,
        deepClone: false,
      },
    ],
    data: {
      tool: { ...tool, id: 2, name: 'compatibleTool' },
      toolVersion: { ...mockToolVersion, id: 2, name: 'compatibleVersion' },
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
      ],
    }),
  ],
};
