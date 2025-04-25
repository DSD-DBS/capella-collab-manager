/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import {
  Breadcrumb,
  BreadcrumbsService,
} from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { BreadcrumbsComponent } from './breadcrumbs.component';

const meta: Meta<BreadcrumbsComponent> = {
  title: 'General Components/Breadcrumbs',
  component: BreadcrumbsComponent,
};

export default meta;
type Story = StoryObj<BreadcrumbsComponent>;

class MockBreadcrumbsService implements Partial<BreadcrumbsService> {
  private readonly _breadcrumbs = new BehaviorSubject<Breadcrumb[]>([]);

  readonly breadcrumbs = this._breadcrumbs.asObservable();

  constructor(breadcrumbs: Breadcrumb[]) {
    this._breadcrumbs.next(breadcrumbs);
  }
}

const mockProjectUserServiceProvider = (breadcrumbs: Breadcrumb[]) => {
  return {
    provide: BreadcrumbsService,
    useValue: new MockBreadcrumbsService(breadcrumbs),
  };
};

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectUserServiceProvider([
          { label: 'Projects', url: '' },
          { label: 'Coffee Machine', url: '' },
          { label: 'coffee-machine', url: '' },
        ]),
      ],
    }),
  ],
};
