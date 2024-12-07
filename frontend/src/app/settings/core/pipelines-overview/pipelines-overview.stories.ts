/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import {
  mockGeneralHealthBad,
  mockGeneralHealthGood,
  mockProjectStatusesBad,
  mockProjectStatusesGood,
  mockToolmodelStatusesBad,
  mockToolmodelStatusesGood,
} from '../../../../storybook/monitoring';
import { PipelinesOverviewComponent } from './pipelines-overview.component';

const meta: Meta<PipelinesOverviewComponent> = {
  title: 'Settings Components/Pipelines Overview',
  component: PipelinesOverviewComponent,
};

export default meta;
type Story = StoryObj<PipelinesOverviewComponent>;

export const Loading: Story = {
  args: {},
};

export const GoodHealth: Story = {
  args: {
    generalHealth: mockGeneralHealthGood,
    toolmodelStatuses: mockToolmodelStatusesGood,
    projectStatuses: mockProjectStatusesGood,
  },
};

export const BadHealth: Story = {
  args: {
    generalHealth: mockGeneralHealthBad,
    toolmodelStatuses: mockToolmodelStatusesBad,
    projectStatuses: mockProjectStatusesBad,
  },
};
