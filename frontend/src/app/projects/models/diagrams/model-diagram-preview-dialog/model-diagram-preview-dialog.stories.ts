/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import MockDate from 'mockdate';
import { dialogWrapper } from 'src/storybook/decorators';
import { base64ModelDiagram } from 'src/storybook/diagram';
import { ModelDiagramPreviewDialogComponent } from './model-diagram-preview-dialog.component';

const meta: Meta<ModelDiagramPreviewDialogComponent> = {
  title: 'Model Components/Diagram Cache Preview',
  component: ModelDiagramPreviewDialogComponent,
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
            content: base64ModelDiagram,
          },
        },
      ],
    }),
    dialogWrapper,
  ],
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
};

export default meta;
type Story = StoryObj<ModelDiagramPreviewDialogComponent>;

export const Loaded: Story = {
  args: {},
};
