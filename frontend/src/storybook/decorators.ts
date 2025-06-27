/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { componentWrapperDecorator } from '@storybook/angular';

export const dialogWrapper = componentWrapperDecorator(
  (story) =>
    `<div class="flex h-screen">
      <div class="rounded-material border m-auto shadow-sm bg-white w-fit max-w-full max-h-full overflow-y-auto">
      ${story}
      </div>
    </div>`,
);
