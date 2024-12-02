/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { mockMetadata } from 'src/storybook/metadata';
import { mockModel } from 'src/storybook/model';
import { mockProject } from 'src/storybook/project';
import { ModelDiagramCodeBlockComponent } from './model-diagram-code-block.component';

const meta: Meta<ModelDiagramCodeBlockComponent> = {
  title: 'Model Components/Model Diagram Code Block',
  component: ModelDiagramCodeBlockComponent,
};

export default meta;
type Story = StoryObj<ModelDiagramCodeBlockComponent>;

export const CodeBlock: Story = {
  args: {
    model: mockModel,
    project: mockProject,
    expanded: true,
    metadata: mockMetadata,
  },
};

export const CodeBlockWithToken: Story = {
  args: {
    model: mockModel,
    project: mockProject,
    expanded: true,
    passwordValue: 'verysecretpassword',
    metadata: mockMetadata,
  },
};

export const CodeBlockWithJobID: Story = {
  args: {
    model: mockModel,
    project: mockProject,
    expanded: true,
    jobId: '1234',
    metadata: mockMetadata,
  },
};
