/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { PathNode } from 'src/app/sessions/service/session.service';
import { FileBrowserDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/file-browser-dialog/file-browser-dialog.component';
import { dialogWrapper } from 'src/storybook/decorators';
import { startedSession } from 'src/storybook/session';

const meta: Meta<FileBrowserDialogComponent> = {
  title: 'Session Components / File Browser',
  component: FileBrowserDialogComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: { session: startedSession },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export default meta;
type Story = StoryObj<FileBrowserDialogComponent>;

export const LoadingFiles: Story = {
  args: {
    loadingFiles: true,
  },
};

export const Files: Story = {
  args: {
    loadingFiles: false,
    dataSource: new BehaviorSubject<PathNode[]>([
      {
        path: '/workspace',
        name: 'workspace',
        type: 'directory',
        isNew: false,
        children: [
          {
            path: '/workspace/file1',
            name: 'file1',
            type: 'file',
            isNew: false,
            children: null,
          },
          {
            path: '/workspace/file2',
            name: 'file2',
            type: 'file',
            isNew: false,
            children: null,
          },
        ],
      },
    ]),
  },
};

export const UploadNewFile: Story = {
  args: {
    loadingFiles: false,
    dataSource: new BehaviorSubject<PathNode[]>([
      {
        path: '/workspace',
        name: 'workspace',
        type: 'directory',
        isNew: false,
        children: [
          {
            path: '/workspace/file1',
            name: 'file1',
            type: 'file',
            isNew: true,
            children: null,
          },
          {
            path: '/workspace/file2',
            name: 'file2',
            type: 'file',
            isNew: false,
            children: null,
          },
        ],
      },
    ]),
  },
};

export const UploadInProgress: Story = {
  args: {
    loadingFiles: false,
    uploadProgress: 30,
  },
};

export const UploadProcessedByBackend: Story = {
  args: {
    loadingFiles: false,
    uploadProgress: 100,
  },
};

export const DownloadPreparation: Story = {
  args: {
    loadingFiles: false,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            ...startedSession,
            download_in_progress: true,
          },
        },
      ],
    }),
  ],
};
