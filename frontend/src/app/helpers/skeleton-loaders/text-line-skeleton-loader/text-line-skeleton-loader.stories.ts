/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { TextLineSkeletonLoaderComponent } from './text-line-skeleton-loader.component';

const meta: Meta<TextLineSkeletonLoaderComponent> = {
  title: 'Helpers / Skeleton Loaders / Text Line',
  component: TextLineSkeletonLoaderComponent,
};

export default meta;
type Story = StoryObj<TextLineSkeletonLoaderComponent>;

export const FullLine: Story = {
  args: {
    width: '100%',
  },
};

export const DefaultLine: Story = {
  args: {},
};

export const ShortLine: Story = {
  args: {
    width: '30%',
  },
};
