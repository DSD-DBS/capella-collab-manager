/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { mockModel } from 'src/storybook/model';
import { mockCapellaToolVersion } from 'src/storybook/tool';
import { CreateReadonlySessionComponent } from './create-readonly-session.component';

const meta: Meta<CreateReadonlySessionComponent> = {
  title: 'Session Components/Create Readonly Session',
  component: CreateReadonlySessionComponent,
};

export default meta;
type Story = StoryObj<CreateReadonlySessionComponent>;

export const Loading: Story = {
  args: {},
};

export const Loaded: Story = {
  args: {
    relevantToolVersions: [mockCapellaToolVersion],
    models: [{ ...mockModel, compatibleVersions: [] }],
  },
};
