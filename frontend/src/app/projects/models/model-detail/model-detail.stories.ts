/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { MockGitModelService, mockPrimaryGitModel } from 'src/storybook/git';
import { mockModel, MockModelWrapperService } from 'src/storybook/model';
import { mockT4CModel, MockT4CModelService } from 'src/storybook/t4c';
import { mockUser, MockOwnUserWrapperService } from 'src/storybook/user';
import { ModelDetailComponent } from './model-detail.component';

const meta: Meta<ModelDetailComponent> = {
  title: 'Model Components/Model Sources/Overview',
  component: ModelDetailComponent,
  parameters: {
    chromatic: { viewports: [1920] },
  },
};

export default meta;
type Story = StoryObj<ModelDetailComponent>;

export const Loading: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ModelWrapperService,
          useFactory: () => new MockModelWrapperService(mockModel, []),
        },
      ],
    }),
  ],
};

export const LoadingAsAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ModelWrapperService,
          useFactory: () => new MockModelWrapperService(mockModel, []),
        },
        {
          provide: OwnUserWrapperService,
          useFactory: () =>
            new MockOwnUserWrapperService({
              ...mockUser,
              role: 'administrator',
            }),
        },
      ],
    }),
  ],
};

export const WithRepositoryAsAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ModelWrapperService,
          useFactory: () => new MockModelWrapperService(mockModel, []),
        },
        {
          provide: OwnUserWrapperService,
          useFactory: () =>
            new MockOwnUserWrapperService({
              ...mockUser,
              role: 'administrator',
            }),
        },
        {
          provide: GitModelService,
          useFactory: () =>
            new MockGitModelService(mockPrimaryGitModel, [
              mockPrimaryGitModel,
              { ...mockPrimaryGitModel, id: 2, primary: false, username: '' },
            ]),
        },
        {
          provide: GitModelService,
          useFactory: () =>
            new MockGitModelService(mockPrimaryGitModel, [
              mockPrimaryGitModel,
              { ...mockPrimaryGitModel, id: 2, primary: false, username: '' },
            ]),
        },
        {
          provide: T4CModelService,
          useFactory: () =>
            new MockT4CModelService(mockT4CModel, [mockT4CModel]),
        },
      ],
    }),
  ],
};
