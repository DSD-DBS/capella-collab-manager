/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { FormFieldSkeletonLoaderComponent } from './form-field-skeleton-loader.component';

const meta: Meta<FormFieldSkeletonLoaderComponent> = {
  title: 'Helpers / Skeleton Loaders / Form Field',
  component: FormFieldSkeletonLoaderComponent,
};

export default meta;
type Story = StoryObj<FormFieldSkeletonLoaderComponent>;

export const Loading: Story = {
  args: {},
};

export const DoneLoading: Story = {
  args: {
    loading: false,
  },
};
