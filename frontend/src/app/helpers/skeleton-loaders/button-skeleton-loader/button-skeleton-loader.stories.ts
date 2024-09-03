/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { ButtonSkeletonLoaderComponent } from './button-skeleton-loader.component';

const meta: Meta<ButtonSkeletonLoaderComponent> = {
  title: 'Helpers / Skeleton Loaders / Button',
  component: ButtonSkeletonLoaderComponent,
};

export default meta;
type Story = StoryObj<ButtonSkeletonLoaderComponent>;

export const Loading: Story = {
  args: {},
};

export const DoneLoading: Story = {
  args: {
    loading: false,
  },
};
