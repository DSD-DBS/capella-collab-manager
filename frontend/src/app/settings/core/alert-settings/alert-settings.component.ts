/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
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
import { MatExpansionModule } from '@angular/material/expansion';
import { MatError, MatFormFieldModule } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { NoticeWrapperService } from 'src/app/general/notice/notice.service';
import {
  CreateNoticeRequest,
  NoticeLevel,
  NoticesService,
} from 'src/app/openapi';

@Component({
  selector: 'app-alert-settings',
  templateUrl: './alert-settings.component.html',
  styleUrls: ['./alert-settings.component.css'],
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInput,
    MatSelect,
    MatOption,
    MatError,
    MatButton,
    MatExpansionModule,
    AsyncPipe,
    NgxSkeletonLoaderModule,
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

  get noticeLevels(): string[] {
    return Object.values(NoticeLevel);
  }

  constructor(
    public noticeWrapperService: NoticeWrapperService,
    private noticeService: NoticesService,
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
        .createNotice(this.createAlertForm.value as CreateNoticeRequest)
        .subscribe({
          next: () => {
            this.noticeWrapperService.refreshNotices();
          },
        });
    }
  }

  deleteNotice(id: number): void {
    this.noticeService.deleteNotice(id).subscribe({
      next: () => {
        this.noticeWrapperService.refreshNotices();
      },
    });
  }
}
