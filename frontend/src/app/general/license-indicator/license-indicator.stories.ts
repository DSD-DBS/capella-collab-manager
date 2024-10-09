/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { PublicLicenseServerWithUsage } from '../../openapi';
import { LicenseIndicatorComponent } from './license-indicator.component';
import { LicenseUsageWrapperService } from './license-usage.service';

const meta: Meta<LicenseIndicatorComponent> = {
  title: 'General Components/License Indicator',
  component: LicenseIndicatorComponent,
};

export default meta;
type Story = StoryObj<LicenseIndicatorComponent>;

class MockLicenseUsageWrapperService
  implements Partial<LicenseUsageWrapperService>
{
  private _licenseServerUsage = new BehaviorSubject<
    PublicLicenseServerWithUsage[] | undefined
  >(undefined);
  readonly licenseServerUsage$ = this._licenseServerUsage.asObservable();
  constructor(licenseServerUsage: PublicLicenseServerWithUsage[]) {
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
              },
            ]),
        },
      ],
    }),
  ],
};
