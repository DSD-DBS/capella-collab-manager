/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpEvent, HttpResponse } from '@angular/common/module.d-CnjH8Dlt';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { Observable, of } from 'rxjs';
import { Tag, TagsService } from 'src/app/openapi';
import { mockProjectTag, mockProjectTag2 } from 'src/storybook/tags';
import { userEvent, within } from 'storybook/test';
import { TagsComponent } from './tags.component';

const meta: Meta<TagsComponent> = {
  title: 'Settings Components/Tags',
  component: TagsComponent,
};

export default meta;
type Story = StoryObj<TagsComponent>;

export const CreateWithInput: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const nameInput = canvas.getByTestId('name-input');
    await userEvent.type(nameInput, 'Example tag');
    const bgColor = canvas.getByTestId('hex-color-input');
    await userEvent.clear(bgColor);
    await userEvent.type(bgColor, '#00008B');
  },
};

class MockTagsService implements Partial<TagsService> {
  tags: Tag[];

  public getTags(): Observable<Tag[]>;
  public getTags(): Observable<HttpResponse<Tag[]>>;
  public getTags(): Observable<HttpEvent<Tag[]>>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public getTags(): Observable<any> {
    return of(this.tags);
  }

  constructor(tags: Tag[]) {
    this.tags = tags;
  }
}

const mockTagsServiceProvider = (tags: Tag[]) => {
  return {
    provide: TagsService,
    useValue: new MockTagsService(tags),
  };
};

export const ExistingTags: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockTagsServiceProvider([mockProjectTag, mockProjectTag2])],
    }),
  ],
};
