/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit } from '@angular/core';
import {
  TokenService,
  Token,
} from 'src/app/general/auth/basic-auth-service/basic-auth-token.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';

@Component({
  selector: 'app-token-settings',
  templateUrl: './basic-auth-token.component.html',
  styleUrls: ['./basic-auth-token.component.css'],
})
export class BasicAuthTokenComponent implements OnInit {
  tokenDescription: string = '';
  password?: string;
  passwordRevealed = false;
  constructor(
    public tokenService: TokenService,
    private toastService: ToastService
  ) {}

  ngOnInit() {
    this.tokenService.loadTokens();
  }

  createNewToken(description?: string) {
    if (!description) {
      description = this.tokenDescription;
    }
    description = 'Token-overview-' + description;
    this.tokenService
      .createToken(description)
      .subscribe((token) => (this.password = token.replaceAll('"', '')));
    this.tokenDescription = '';
  }

  deleteToken(token: Token) {
    this.tokenService.deleteToken(token).subscribe();
  }

  isTokenExpired(expirationDate: string): boolean {
    const expirationDateObj = new Date(expirationDate);
    return expirationDateObj < new Date();
  }

  showClipboardMessage(): void {
    this.toastService.showSuccess(
      'Token copied',
      'The token was copied to your clipboard.'
    );
  }
}
