/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Pipeline } from 'src/app/openapi';
import { mockPrimaryGitModel } from 'src/storybook/git';
import { mockT4CModel } from 'src/storybook/t4c';

export const mockBackup: Pipeline = {
  id: 1,
  t4c_model: mockT4CModel,
  git_model: mockPrimaryGitModel,
  run_nightly: false,
  next_run: null,
};
