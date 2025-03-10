/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import MockDate from 'mockdate';
import { dialogWrapper } from 'src/storybook/decorators';
import {
  base64LargeModelDiagram,
  base64SmallModelDiagram,
} from 'src/storybook/diagram';
import { ModelDiagramPreviewDialogComponent } from './model-diagram-preview-dialog.component';

const meta: Meta<ModelDiagramPreviewDialogComponent> = {
  title: 'Model Components/Diagram Cache Preview',
  component: ModelDiagramPreviewDialogComponent,
  decorators: [dialogWrapper],
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<ModelDiagramPreviewDialogComponent>;

export const LargeDiagram: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            diagram: {
              name: 'Example diagram',
              uuid: '_yYhrh3jqEea__MYrXGSERA',
              success: true,
            },
            content: base64LargeModelDiagram,
          },
        },
      ],
    }),
  ],
};

export const SmallDiagram: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            diagram: {
              name: 'Example diagram',
              uuid: '_yYhrh3jqEea__MYrXGSERA',
              success: true,
            },
            content: base64SmallModelDiagram,
          },
        },
      ],
    }),
  ],
};
