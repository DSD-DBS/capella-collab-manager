/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';

import {
  ProjectUserRole,
  ProjectUserService,
} from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { Project } from 'src/app/projects/service/project.service';
import { ProjectMetadataComponent } from './project-metadata.component';

class MockProjectUserService implements Partial<ProjectUserService> {
  user: ProjectUserRole;

  constructor(user: ProjectUserRole) {
    this.user = user;
  }

  verifyRole(requiredRole: ProjectUserRole): boolean {
    const roles = ['user', 'manager', 'administrator'];
    return roles.indexOf(requiredRole) <= roles.indexOf(this.user);
  }
}

const meta: Meta<ProjectMetadataComponent> = {
  title: 'Project Components / Project Metadata',
  component: ProjectMetadataComponent,
};

export default meta;
type Story = StoryObj<ProjectMetadataComponent>;

const project: Project = {
  name: 'test',
  description: 'test',
  type: 'general',
  visibility: 'internal',
  is_archived: false,
  slug: 'test',
  users: {
    leads: 1,
    contributors: 1,
    subscribers: 1,
  },
};

export const Loading: Story = {
  args: {
    project: undefined,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('user'),
        },
      ],
    }),
  ],
};

export const NormalUser: Story = {
  args: {
    project: project,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('user'),
        },
      ],
    }),
  ],
};

export const ProjectAdmin: Story = {
  args: {
    project: project,
    canDelete: true,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('manager'),
        },
      ],
    }),
  ],
};

export const Archived: Story = {
  args: {
    project: { ...project, is_archived: true },
    canDelete: true,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('manager'),
        },
      ],
    }),
  ],
};

export const CantDelete: Story = {
  args: {
    project: project,
    canDelete: false,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('manager'),
        },
      ],
    }),
  ],
};
