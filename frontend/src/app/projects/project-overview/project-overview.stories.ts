/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { ProjectFavoritesService } from './project-favorites.service';
import { ProjectOverviewComponent } from './project-overview.component';

const mockFavoritesServiceProvider = (favorites: number[] = []) => ({
  provide: ProjectFavoritesService,
  useValue: {
    isFavorite: (id: number) => favorites.includes(id),
  },
});

const meta: Meta<ProjectOverviewComponent> = {
  title: 'Project Components/Project Overview',
  component: ProjectOverviewComponent,
};

export default meta;
type Story = StoryObj<ProjectOverviewComponent>;

export const Loading: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockFavoritesServiceProvider()],
    }),
  ],
};

export const Overview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(undefined, [
          {
            ...mockProject,
            name: 'Internal project',
            visibility: 'internal',
          },
          {
            ...mockProject,
            name: 'Private project',
            visibility: 'private',
          },
          {
            ...mockProject,
            name: 'Training project',
            type: 'training',
          },
          {
            ...mockProject,
            name: 'Project with more users',
            users: {
              leads: 16,
              contributors: 24,
              subscribers: 106,
            },
          },
          {
            ...mockProject,
            name: 'Archived project',
            is_archived: true,
          },
          {
            ...mockProject,
            name: 'Project without description',
            description: '',
          },
          {
            ...mockProject,
            name: 'This is a very long project name. Why would someone name a project like this?',
            is_archived: true,
          },
        ]),
        mockFavoritesServiceProvider(),
      ],
    }),
  ],
};

export const WithFavorites: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(undefined, [
          {
            ...mockProject,
            id: 1,
            name: 'Favorite Internal project',
            visibility: 'internal',
          },
          {
            ...mockProject,
            id: 2,
            name: 'Regular Private project',
            visibility: 'private',
          },
          {
            ...mockProject,
            id: 3,
            name: 'Favorite Training project',
            type: 'training',
          },
        ]),
        mockFavoritesServiceProvider([1, 3]), // Mark projects 1 and 3 as favorites
      ],
    }),
  ],
};
