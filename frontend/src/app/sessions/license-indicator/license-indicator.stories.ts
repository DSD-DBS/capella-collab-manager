/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  componentWrapperDecorator,
  Meta,
  moduleMetadata,
  StoryObj,
} from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { T4CLicenseServer } from '../../openapi';
import { LicenseIndicatorComponent } from './license-indicator.component';
import { LicenseUsageWrapperService } from './license-usage.service';

const meta: Meta<LicenseIndicatorComponent> = {
  title: 'Session Components/License Indicator',
  component: LicenseIndicatorComponent,
  decorators: [
    componentWrapperDecorator(
      (story) =>
        `<div class="w-[336px] sm:w-[426px]">
          ${story}
        </div>`,
    ),
  ],
};

export default meta;
type Story = StoryObj<LicenseIndicatorComponent>;

export class MockLicenseUsageWrapperService
  implements Partial<LicenseUsageWrapperService>
{
  private _licenseServerUsage = new BehaviorSubject<
    T4CLicenseServer[] | undefined
  >(undefined);
  readonly licenseServerUsage$ = this._licenseServerUsage.asObservable();
  constructor(licenseServerUsage: T4CLicenseServer[]) {
    this._licenseServerUsage.next(licenseServerUsage);
  }
}

export const AllUsed: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: LicenseUsageWrapperService,
          useFactory: () =>
            new MockLicenseUsageWrapperService([
              {
                id: 1,
                name: 'Test',
                usage: {
                  free: 0,
                  total: 30,
                },
                license_server_version: '',
                license_key: '',
                usage_api: '',
                instances: [],
                warnings: [],
              },
            ]),
        },
      ],
    }),
  ],
};

export const SomeUsed: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: LicenseUsageWrapperService,
          useFactory: () =>
            new MockLicenseUsageWrapperService([
              {
                id: 1,
                name: 'Test',
                usage: {
                  free: 5,
                  total: 30,
                },
                license_server_version: '',
                license_key: '',
                usage_api: '',
                instances: [],
                warnings: [],
              },
            ]),
        },
      ],
    }),
  ],
};

export const FewUsed: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: LicenseUsageWrapperService,
          useFactory: () =>
            new MockLicenseUsageWrapperService([
              {
                id: 1,
                name: 'Test',
                usage: {
                  free: 25,
                  total: 30,
                },
                license_server_version: '',
                license_key: '',
                usage_api: '',
                instances: [],
                warnings: [],
              },
            ]),
        },
      ],
    }),
  ],
};
