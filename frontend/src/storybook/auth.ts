/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';

class MockAuthenticationWrapperService
  implements Partial<AuthenticationWrapperService>
{
  isLoggedIn(): boolean {
    return true;
  }
}

export const mockAuthenticationWrapperServiceProvider = () => {
  return {
    provide: AuthenticationWrapperService,
    useValue: new MockAuthenticationWrapperService(),
  };
};
