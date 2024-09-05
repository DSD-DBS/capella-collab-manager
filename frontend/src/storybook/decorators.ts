/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { componentWrapperDecorator } from '@storybook/angular';

export const dialogWrapper = componentWrapperDecorator(
  (story) =>
    `<div class="rounded-md border shadow bg-white w-fit">${story}</div>`,
);
