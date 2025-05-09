/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { componentWrapperDecorator, Meta, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { TagComponent } from './tag.component';

const meta: Meta<TagComponent> = {
  title: 'Helpers/Tag Component',
  component: TagComponent,
};

export default meta;
type Story = StoryObj<TagComponent>;

export const TagWithActionAndIcon: Story = {
  args: {
    hexBgColor: '#FF5733',
    name: 'Example Tag',
    description: 'This is an example tag description.',
    textIcon: 'experiment',
    actionIcon: 'edit',
  },
  decorators: [componentWrapperDecorator((story) => `${story}`)],
};

export const TagWithActionWithoutIcon: Story = {
  args: {
    hexBgColor: '#add8e6',
    name: 'Example Tag without icon',
    description: 'This is an example tag description.',
    actionIcon: 'delete',
  },
  decorators: [componentWrapperDecorator((story) => `${story}`)],
};

export const StandaloneTagHover: Story = {
  args: {
    hexBgColor: '#000000',
    name: 'Example Tag without icon/action',
    description: 'This is an example tag description.',
  },
  decorators: [componentWrapperDecorator((story) => `${story}`)],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const tag = canvas.getByTestId('tag');
    await userEvent.hover(tag);
  },
};
