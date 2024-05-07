/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';

export const mockPrimaryGitModel: Readonly<GetGitModel> = {
  id: 1,
  primary: true,
  path: 'fakePath',
  revision: 'fakeRevision',
  entrypoint: 'fakeEntrypoint',
  password: false,
  username: 'fakeUsername',
};
