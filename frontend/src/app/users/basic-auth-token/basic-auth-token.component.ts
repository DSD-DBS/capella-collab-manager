/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, DatePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import {
  MatDatepickerInput,
  MatDatepickerToggle,
  MatDatepicker,
} from '@angular/material/datepicker';
import {
  MatFormField,
  MatLabel,
  MatHint,
  MatSuffix,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { UserToken } from 'src/app/openapi';
import { TokenService } from 'src/app/users/basic-auth-service/basic-auth-token.service';
import { DisplayValueComponent } from '../../helpers/display-value/display-value.component';

@Component({
  selector: 'app-token-settings',
  templateUrl: './basic-auth-token.component.html',
  styleUrls: ['./basic-auth-token.component.css'],
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatHint,
    MatDatepickerInput,
    MatDatepickerToggle,
    MatSuffix,
    MatDatepicker,
    MatButton,
    DisplayValueComponent,
    MatIcon,
    AsyncPipe,
    DatePipe,
  ],
})
export class BasicAuthTokenComponent implements OnInit {
  password?: string;
  passwordRevealed = false;
  minDate: Date;
  maxDate: Date;

  tokenForm = this.formBuilder.group({
    description: ['', [Validators.required, Validators.minLength(1)]],
    date: [this.getTomorrow(), [Validators.required]],
  });
  constructor(
    public tokenService: TokenService,
    private toastService: ToastService,
    private formBuilder: FormBuilder,
  ) {
    this.minDate = this.getTomorrow();
    this.maxDate = new Date(
      this.minDate.getFullYear() + 1,
      this.minDate.getMonth(),
      this.minDate.getDate(),
    );
  }

  ngOnInit() {
    this.tokenService.loadTokens();
  }

  getTomorrow(): Date {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow;
  }

  createToken(): void {
    if (this.tokenForm.valid) {
      this.tokenService
        .createToken(
          this.tokenForm.value.description!,
          this.tokenForm.value.date!,
          'Token-overview',
        )
        .subscribe((token) => {
          this.password = token.password;
          this.tokenForm.controls.date.setValue(this.getTomorrow());
        });
    }
  }

  deleteToken(token: UserToken) {
    this.tokenService.deleteToken(token).subscribe();
    this.toastService.showSuccess(
      'Token deleted',
      `The token ${token.description} was successfully deleted!`,
    );
  }

  isTokenExpired(expirationDate: string): boolean {
    return new Date(expirationDate) < new Date();
  }

  showClipboardMessage(): void {
    this.toastService.showSuccess(
      'Token copied',
      'The token was copied to your clipboard.',
    );
  }
}
