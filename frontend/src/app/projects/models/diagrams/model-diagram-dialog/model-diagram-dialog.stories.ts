/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import MockDate from 'mockdate';
import { DiagramCacheMetadata } from 'src/app/openapi';
import { dialogWrapper } from 'src/storybook/decorators';
import { base64ModelDiagram } from 'src/storybook/diagram';
import { mockModel } from 'src/storybook/model';
import { mockProject } from 'src/storybook/project';
import {
  Diagrams,
  ModelDiagramDialogComponent,
} from './model-diagram-dialog.component';

const meta: Meta<ModelDiagramDialogComponent> = {
  title: 'Model Components/Model Diagram Cache',
  component: ModelDiagramDialogComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: { model: mockModel, project: mockProject },
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
type Story = StoryObj<ModelDiagramDialogComponent>;

const emptyDiagramCacheMetadata: DiagramCacheMetadata = {
  diagrams: [],
  last_updated: '2024-04-29T14:00:00Z',
  job_id: null,
};

const loadedDiagramCacheMetadata: DiagramCacheMetadata = {
  diagrams: [{ name: 'fakeDiagram1', uuid: 'fakeUUID-Loaded', success: true }],
  last_updated: '2024-04-29T14:00:00Z',
  job_id: null,
};

const notLoadedDiagramCacheMetadata: DiagramCacheMetadata = {
  diagrams: [
    { name: 'fakeDiagram2', uuid: 'fakeUUID-Not-Loaded', success: true },
  ],
  last_updated: '2024-04-29T14:00:00Z',
  job_id: null,
};

const errorDiagramCacheMetadata: DiagramCacheMetadata = {
  diagrams: [{ name: 'fakeDiagram3', uuid: 'fakeUUID-Loaded', success: false }],
  last_updated: '2024-04-29T14:00:00Z',
  job_id: null,
};

const combinedDiagramCacheMetadata: DiagramCacheMetadata = {
  diagrams: [
    { name: 'fakeDiagram1', uuid: 'fakeUUID-Loaded', success: true },
    { name: 'fakeDiagram2', uuid: 'fakeUUID-Not-Loaded', success: true },
    { name: 'fakeDiagram3', uuid: 'fakeUUID-Loaded', success: false },
  ],
  last_updated: '2024-04-29T14:00:00Z',
  job_id: null,
};

// prettier-ignore
const diagrams: Diagrams =
  {
    "fakeUUID-Loaded": {
      loading: false,
      content: base64ModelDiagram,
    },
    "fakeUUID-Not-Loaded": {
      loading: true,
      content: base64ModelDiagram,
    }
  }

export const Loading: Story = {
  args: { diagramMetadata: undefined },
};

export const LoadingWithoutScroll: Story = {
  args: { diagramMetadata: undefined, loaderArray: Array(3).fill(0) },
};

export const DiagramLoaded: Story = {
  args: {
    diagramMetadata: loadedDiagramCacheMetadata,
    diagrams: diagrams,
  },
};

export const DiagramNotLoaded: Story = {
  args: {
    diagramMetadata: notLoadedDiagramCacheMetadata,
    diagrams: diagrams,
  },
};

export const DiagramError: Story = {
  args: {
    diagramMetadata: errorDiagramCacheMetadata,
    diagrams: diagrams,
  },
};

export const Combined: Story = {
  args: {
    diagramMetadata: combinedDiagramCacheMetadata,
    diagrams: diagrams,
  },
};

export const NoDiagram: Story = {
  args: { diagramMetadata: emptyDiagramCacheMetadata },
};

export const NoDiagramForFilter: Story = {
  args: {
    diagramMetadata: loadedDiagramCacheMetadata,
    diagrams: diagrams,
    search: 'random filter',
  },
};
