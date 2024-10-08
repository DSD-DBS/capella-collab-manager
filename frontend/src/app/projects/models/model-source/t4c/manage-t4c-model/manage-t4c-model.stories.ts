/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { T4CRepositoryWrapperService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { mockModel, MockModelWrapperService } from 'src/storybook/model';
import { mockProject, MockProjectWrapperService } from 'src/storybook/project';
import {
  mockExtendedT4CRepository,
  mockT4CInstance,
  mockT4CModel,
  MockT4CModelService,
  MockT4CRepositoryWrapperService,
} from 'src/storybook/t4c';
import { ManageT4CModelComponent } from './manage-t4c-model.component';

const meta: Meta<ManageT4CModelComponent> = {
  title: 'Model Components/Model Sources/Update T4C Model',
  component: ManageT4CModelComponent,
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
type Story = StoryObj<ManageT4CModelComponent>;

export const Loading: Story = {
  args: {},
};

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CModelService,
          useFactory: () =>
            new MockT4CModelService(undefined, undefined, [mockT4CInstance]),
        },
        {
          provide: T4CRepositoryWrapperService,
          useFactory: () =>
            new MockT4CRepositoryWrapperService([mockExtendedT4CRepository]),
        },
      ],
    }),
  ],
};

export const NoRepository: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    await userEvent.click(within(canvasElement).getByTestId('t4c-instance'));

    const generalDropdownItem = document.querySelector(
      'mat-option[ng-reflect-value="1"]',
    );
    if (!generalDropdownItem) {
      throw new Error('Dropdown item with value "1" not found');
    }
    await userEvent.click(generalDropdownItem);
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CModelService,
          useFactory: () =>
            new MockT4CModelService(undefined, undefined, [mockT4CInstance]),
        },
        {
          provide: T4CRepositoryWrapperService,
          useFactory: () => new MockT4CRepositoryWrapperService([]),
        },
      ],
    }),
  ],
};

export const NoInstances: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CModelService,
          useFactory: () => new MockT4CModelService(undefined, undefined, []),
        },
      ],
    }),
  ],
};

export const Modify: Story = {
  args: {
    t4cModel: mockT4CModel,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CModelService,
          useFactory: () =>
            new MockT4CModelService(mockT4CModel, undefined, [mockT4CInstance]),
        },
        {
          provide: T4CRepositoryWrapperService,
          useFactory: () =>
            new MockT4CRepositoryWrapperService([mockExtendedT4CRepository]),
        },
      ],
    }),
  ],
};
