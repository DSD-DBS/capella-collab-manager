/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { PageNotFoundComponent } from './404.component';

const meta: Meta<PageNotFoundComponent> = {
  title: 'General Components/404 (Not Found)',
  component: PageNotFoundComponent,
};

export default meta;
type Story = StoryObj<PageNotFoundComponent>;

export const NotFound: Story = {};
