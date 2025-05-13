/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Tag, TagScope } from 'src/app/openapi';

export const mockProjectTag: Tag = {
  id: 1,
  name: 'Open Classification',
  hex_color: '#075200',
  icon: 'public',
  description: null,
  scope: TagScope.Project,
};

export const mockProjectTag2: Tag = {
  id: 2,
  name: 'Storybook',
  hex_color: '#fcc2e4',
  icon: 'newspaper',
  description: null,
  scope: TagScope.Project,
};

export const mockUserTag: Tag = {
  id: 3,
  name: 'Storybook',
  hex_color: '#fcc2e4',
  icon: 'newspaper',
  description: null,
  scope: TagScope.User,
};
