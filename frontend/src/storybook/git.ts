/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { GitModel } from 'src/app/openapi';

export const mockPrimaryGitModel: Readonly<GitModel> = {
  id: 1,
  name: 'fakeGitModelName',
  primary: true,
  path: 'fakePath',
  revision: 'fakeRevision',
  entrypoint: 'fakeEntrypoint',
  password: false,
  username: 'fakeUsername',
};
