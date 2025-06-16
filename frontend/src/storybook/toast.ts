/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { ToastService } from 'src/app/helpers/toast/toast.service';

export class MockToastService implements Partial<ToastService> {
  showSuccess(title: string, message: string) {
    // eslint-disable-next-line no-console
    console.log(`[MOCK SUCCESS] ${title}: ${message}`);
  }
  showError(title: string, message: string) {
    // eslint-disable-next-line no-console
    console.log(`[MOCK ERROR] ${title}: ${message}`);
  }
  showWarning(title: string, message: string) {
    // eslint-disable-next-line no-console
    console.log(`[MOCK WARNING] ${title}: ${message}`);
  }
}

export const mockToastServiceProvider = {
  provide: ToastService,
  useClass: MockToastService,
};
