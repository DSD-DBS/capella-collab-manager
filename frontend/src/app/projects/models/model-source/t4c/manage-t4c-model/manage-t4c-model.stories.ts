/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import { T4CRepositoryWrapperService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { mockModel, MockModelWrapperService } from 'src/storybook/model';
import { mockProject, MockProjectWrapperService } from 'src/storybook/project';
import {
  mockExtendedT4CRepository,
  mockT4CInstance,
  MockT4CInstanceWrapperService,
  MockT4CRepositoryWrapperService,
} from 'src/storybook/t4c';
import { ManageT4CModelComponent } from './manage-t4c-model.component';

const meta: Meta<ManageT4CModelComponent> = {
  title: 'Model Components / Model Sources / T4C',
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
          provide: T4CInstanceWrapperService,
          useFactory: () =>
            new MockT4CInstanceWrapperService(mockT4CInstance, [
              mockT4CInstance,
            ]),
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
