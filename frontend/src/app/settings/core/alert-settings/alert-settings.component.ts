/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgFor, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import {
  MatAccordion,
  MatExpansionPanel,
  MatExpansionPanelHeader,
  MatExpansionPanelTitle,
  MatExpansionPanelDescription,
} from '@angular/material/expansion';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  CreateNotice,
  NoticeService,
} from 'src/app/services/notice/notice.service';

@Component({
  selector: 'app-alert-settings',
  templateUrl: './alert-settings.component.html',
  styleUrls: ['./alert-settings.component.css'],
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatSelect,
    NgFor,
    MatOption,
    MatError,
    NgIf,
    MatButton,
    MatAccordion,
    MatExpansionPanel,
    MatExpansionPanelHeader,
    MatExpansionPanelTitle,
    MatExpansionPanelDescription,
  ],
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
