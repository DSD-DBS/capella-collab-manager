/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Project } from 'src/app/projects/service/project.service';

export const mockProject: Readonly<Project> = {
  name: 'mockProject',
  description:
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
  type: 'general',
  visibility: 'internal',
  is_archived: false,
  slug: 'mockProject',
  users: {
    leads: 1,
    contributors: 1,
    subscribers: 1,
  },
};
