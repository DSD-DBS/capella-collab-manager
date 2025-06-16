/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { ToastrService } from 'ngx-toastr';

@Injectable({
  providedIn: 'root',
})
export class ToastService {
  private toastr = inject(ToastrService);

  showSuccess(title: string, message: string) {
    this.toastr.success(message, title);
  }

  showError(title: string, message: string) {
    this.toastr.error(message, title);
  }

  showWarning(title: string, message: string) {
    this.toastr.warning(message, title);
  }
}
