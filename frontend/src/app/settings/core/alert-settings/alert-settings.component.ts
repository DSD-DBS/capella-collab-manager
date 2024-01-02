/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  CreateNotice,
  NoticeService,
} from 'src/app/services/notice/notice.service';

@Component({
  selector: 'app-alert-settings',
  templateUrl: './alert-settings.component.html',
  styleUrls: ['./alert-settings.component.css'],
})
export class AlertSettingsComponent {
  createAlertForm = new FormGroup(
    {
      title: new FormControl(''),
      message: new FormControl(''),
      level: new FormControl('', Validators.required),
    },
    this.titleOrDescriptionRequired(),
  );

  get message(): FormControl {
    return this.createAlertForm.get('message') as FormControl;
  }

  constructor(
    public noticeService: NoticeService,
    private toastService: ToastService,
  ) {}

  titleOrDescriptionRequired(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (control.get('title')?.value || control.get('message')?.value) {
        control.get('message')?.setErrors(null);
        return null;
      }
      control.get('message')?.setErrors({ titleOrDescriptionAvailable: true });
      return { titleOrDescriptionAvailable: true };
    };
  }

  createNotice(): void {
    if (this.createAlertForm.valid) {
      this.noticeService
        .createNotice(this.createAlertForm.value as CreateNotice)
        .subscribe({
          next: () => {
            this.noticeService.refreshNotices();
            this.toastService.showSuccess(
              'Alert created',
              this.createAlertForm.value.title as string,
            );
          },
          error: () => {
            this.toastService.showError(
              'Creation of alert failed',
              'Please try again',
            );
          },
        });
    }
  }

  deleteNotice(id: number): void {
    this.noticeService.deleteNotice(id).subscribe({
      next: () => {
        this.toastService.showSuccess('Alert deleted', 'ID: ' + id);
        this.noticeService.refreshNotices();
      },
      error: () => {
        this.toastService.showSuccess(
          'Deletion of alert failed',
          'Please try again',
        );
      },
    });
  }
}
