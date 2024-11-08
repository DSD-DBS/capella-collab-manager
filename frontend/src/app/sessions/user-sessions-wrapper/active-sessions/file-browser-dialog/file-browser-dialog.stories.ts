/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatTableDataSource } from '@angular/material/table';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { PathNode } from 'src/app/sessions/service/session.service';
import { FileBrowserDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/file-browser-dialog/file-browser-dialog.component';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockPersistentSession } from 'src/storybook/session';

const meta: Meta<FileBrowserDialogComponent> = {
  title: 'Session Components/File Browser',
  component: FileBrowserDialogComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: { session: mockPersistentSession },
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
    dataSource: new MatTableDataSource<PathNode>([
      {
        path: '/workspace',
        name: 'workspace',
        type: 'directory',
        isNew: false,
        isExpanded: true,
        children: [
          {
            path: '/workspace/file1',
            name: 'file1',
            type: 'file',
            children: null,
          },
          {
            path: '/workspace/file2',
            name: 'file2',
            type: 'file',
            children: null,
          },
          {
            path: '/workspace/directory1',
            name: 'directory1',
            type: 'directory',
            isExpanded: true,
            children: [
              {
                path: '/workspace/directory1/file1',
                name: 'file1',
                type: 'file',
                children: null,
              },
              {
                path: '/workspace/directory1/file2',
                name: 'file2',
                type: 'file',
                children: null,
              },
            ],
          },
          {
            path: '/workspace/directory2',
            name: 'directory2',
            type: 'directory',
            children: [],
          },
          {
            path: '/workspace/directory3',
            name: 'directory3',
            type: 'directory',
            children: [],
          },
        ],
      },
    ]),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const folderButton = canvas.getByTestId('folder-button-directory2');

    // Needed to trigger Angular change detection
    await userEvent.click(folderButton);
    await userEvent.click(folderButton);
  },
};

export const UploadNewFile: Story = {
  args: {
    loadingFiles: false,
    dataSource: new MatTableDataSource<PathNode>([
      {
        path: '/workspace',
        name: 'workspace',
        type: 'directory',
        isExpanded: true,
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
            isModified: true,
            children: null,
          },
          {
            path: '/workspace/file3',
            name: 'file3',
            type: 'file',
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
            ...mockPersistentSession,
            download_in_progress: true,
          },
        },
      ],
    }),
  ],
};
