// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { NoticeService } from 'src/app/services/notice/notice.service';

@Component({
  selector: 'app-alert-settings',
  templateUrl: './alert-settings.component.html',
  styleUrls: ['./alert-settings.component.css'],
})
export class AlertSettingsComponent implements OnInit {
  createAlertForm = new FormGroup(
    {
      title: new FormControl(''),
      message: new FormControl(''),
      scope: new FormControl('', Validators.required),
      level: new FormControl('', Validators.required),
    },
    this.titleOrDescriptionRequired()
  );

  get message(): FormControl {
    return this.createAlertForm.get('message') as FormControl;
  }

  constructor(public noticeService: NoticeService) {}

  ngOnInit(): void {}

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
        .createNotice(this.createAlertForm.value)
        .subscribe(() => {
          this.noticeService.refreshNotices();
        });
    }
  }

  deleteNotice(id: number): void {
    this.noticeService.deleteNotice(id).subscribe(() => {
      this.noticeService.refreshNotices();
    });
  }
}
