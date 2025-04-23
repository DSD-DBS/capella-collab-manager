/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockCapellaTool,
  mockCapellaToolVersion,
  mockToolNature,
  mockToolWrapperServiceProvider,
  mockTrainingControllerTool,
} from 'src/storybook/tool';
import { ToolsSettingsComponent } from './tools-settings.component';

const meta: Meta<ToolsSettingsComponent> = {
  title: 'Settings Components/Tools Settings',
  component: ToolsSettingsComponent,
};

export default meta;
type Story = StoryObj<ToolsSettingsComponent>;

export const General: Story = {
  args: {
    tools: {
      [mockCapellaTool.id]: {
        natures: [mockToolNature],
        versions: [mockCapellaToolVersion],
      },
    },
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockToolWrapperServiceProvider([
          mockCapellaTool,
          mockTrainingControllerTool,
        ]),
      ],
    }),
  ],
};
