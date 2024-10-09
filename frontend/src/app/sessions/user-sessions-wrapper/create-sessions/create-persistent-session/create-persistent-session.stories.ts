/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { createPersistentSessionWithState } from '../../../../../storybook/session';
import { LicenseUsageWrapperService } from '../../../../general/license-indicator/license-usage.service';
import { PublicLicenseServerWithUsage, Session } from '../../../../openapi';
import { SessionService } from '../../../service/session.service';
import { UserSessionService } from '../../../service/user-session.service';
import { CreatePersistentSessionComponent } from './create-persistent-session.component';

const meta: Meta<CreatePersistentSessionComponent> = {
  title: 'Session Components/Create Persistent Session',
  component: CreatePersistentSessionComponent,
};

export default meta;
type Story = StoryObj<CreatePersistentSessionComponent>;

// TODO fix duplication
class MockSessionService implements Partial<SessionService> {}
class MockUserSessionService implements Partial<UserSessionService> {
  public readonly sessions$: Observable<Session[] | undefined> = of(undefined);

  constructor(session?: Session, empty?: boolean) {
    if (session !== undefined) {
      this.sessions$ = of([session]);
    } else if (empty === true) {
      this.sessions$ = of([]);
    }
  }
}
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
// End TODO

export const Default: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: SessionService,
          useFactory: () => new MockSessionService(),
        },
        {
          provide: UserSessionService,
          useFactory: () =>
            new MockUserSessionService(
              createPersistentSessionWithState('Started'),
            ),
        },
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
