/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  TokenService,
  Token,
} from 'src/app/users/basic-auth-service/basic-auth-token.service';

@Component({
  selector: 'app-token-settings',
  templateUrl: './basic-auth-token.component.html',
  styleUrls: ['./basic-auth-token.component.css'],
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

  deleteToken(token: Token) {
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
