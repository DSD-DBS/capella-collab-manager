/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { componentWrapperDecorator, Meta, StoryObj } from '@storybook/angular';
import { MatCardOverviewSkeletonLoaderComponent } from './mat-card-overview-skeleton-loader.component';

const meta: Meta<MatCardOverviewSkeletonLoaderComponent> = {
  title: 'Helpers/Skeleton Loaders/Mat Card Overview',
  component: MatCardOverviewSkeletonLoaderComponent,
};

export default meta;
type Story = StoryObj<MatCardOverviewSkeletonLoaderComponent>;

export const General: Story = {
  args: {
    rows: 3,
    reservedCards: 0,
  },
  decorators: [
    componentWrapperDecorator(
      (story) => `<div class="flex flex-wrap gap-5 *:contents">${story}</div>`,
    ),
  ],
};
