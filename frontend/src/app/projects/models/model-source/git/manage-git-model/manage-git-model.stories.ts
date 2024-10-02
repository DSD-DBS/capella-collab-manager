/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { ActivatedRoute } from '@angular/router';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { GitInstancesWrapperService } from 'src/app/settings/modelsources/git-settings/service/git-instances.service';
import {
  mockGitInstance,
  MockGitInstancesService,
  MockGitModelService,
  mockPrimaryGitModel,
} from 'src/storybook/git';
import { mockModel, MockModelWrapperService } from 'src/storybook/model';
import { mockProject, MockProjectWrapperService } from 'src/storybook/project';
import { MockActivedRoute } from 'src/storybook/routes';
import { ManageGitModelComponent } from './manage-git-model.component';

const meta: Meta<ManageGitModelComponent> = {
  title: 'Model Components/Model Sources/Git',
  component: ManageGitModelComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectWrapperService,
          useFactory: () =>
            new MockProjectWrapperService(mockProject, [mockProject]),
        },
        {
          provide: ModelWrapperService,
          useFactory: () => new MockModelWrapperService(mockModel, [mockModel]),
        },
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<ManageGitModelComponent>;

export const InvalidURL: Story = {
  parameters: {
    screenshot: {
      delay: 1000,
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const absoluteURL = canvas.getByTestId('absolute-url');
    const resultingURL = canvas.getByTestId('resulting-url');
    await userEvent.type(absoluteURL, 'invalid-url');
    await userEvent.click(absoluteURL);
    await userEvent.click(resultingURL);
  },
};

export const ValidURL: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const absoluteURL = canvas.getByTestId('absolute-url');
    const resultingURL = canvas.getByTestId('resulting-url');
    await userEvent.type(absoluteURL, 'https://example.com');
    await userEvent.click(absoluteURL);
    await userEvent.click(resultingURL);
  },
};

export const ExistingGitModel: Story = {
  args: {
    resultUrl: 'https://example.com',
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: GitModelService,
          useFactory: () => new MockGitModelService(mockPrimaryGitModel, []),
        },
        {
          provide: ActivatedRoute,
          useFactory: () =>
            new MockActivedRoute({
              'git-model': '-1',
            }),
        },
        {
          provide: GitInstancesWrapperService,
          useFactory: () =>
            new MockGitInstancesService(undefined, [mockGitInstance]),
        },
      ],
    }),
  ],
};

export const ExistingGitModelEditing: Story = {
  args: {
    resultUrl: 'https://example.com',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByTestId('edit'));
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: GitModelService,
          useFactory: () => new MockGitModelService(mockPrimaryGitModel, []),
        },
        {
          provide: ActivatedRoute,
          useFactory: () =>
            new MockActivedRoute({
              'git-model': '-1',
            }),
        },
        {
          provide: GitInstancesWrapperService,
          useFactory: () =>
            new MockGitInstancesService(undefined, [mockGitInstance]),
        },
      ],
    }),
  ],
};
