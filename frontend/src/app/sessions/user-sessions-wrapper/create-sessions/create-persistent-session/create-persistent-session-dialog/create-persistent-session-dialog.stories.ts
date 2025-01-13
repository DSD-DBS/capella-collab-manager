/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import {
  mockCapellaTool,
  mockCapellaToolVersion,
  mockHttpConnectionMethod,
} from '../../../../../../storybook/tool';
import { CreatePersistentSessionDialogComponent } from './create-persistent-session-dialog.component';

const meta: Meta<CreatePersistentSessionDialogComponent> = {
  title: 'Session Components/Create Persistent Session Dialog',
  component: CreatePersistentSessionDialogComponent,
};

export default meta;
type Story = StoryObj<CreatePersistentSessionDialogComponent>;

export const WithConnectionMethodSelection: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            tool: {
              ...mockCapellaTool,
              config: {
                connection: {
                  methods: [mockHttpConnectionMethod, mockHttpConnectionMethod],
                },
              },
            },
            toolVersion: mockCapellaToolVersion,
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export const WithoutConnectionMethodSelection: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            tool: mockCapellaTool,
            toolVersion: mockCapellaToolVersion,
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};
