/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockModel,
  MockModelWrapperService,
} from '../../../../storybook/model';
import {
  mockProject,
  MockProjectWrapperService,
} from '../../../../storybook/project';
import { ProjectWrapperService } from '../../service/project.service';
import { ModelWrapperService } from '../service/model.service';
import { InitModelComponent } from './init-model.component';

const meta: Meta<InitModelComponent> = {
  title: 'Model Components/Init Model',
  component: InitModelComponent,
};

export default meta;
type Story = StoryObj<InitModelComponent>;

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ModelWrapperService,
          useFactory: () => new MockModelWrapperService(mockModel, []),
        },
        {
          provide: ProjectWrapperService,
          useFactory: () =>
            new MockProjectWrapperService(undefined, [
              {
                ...mockProject,
                name: 'Internal project',
                visibility: 'internal',
              },
            ]),
        },
      ],
    }),
  ],
};
