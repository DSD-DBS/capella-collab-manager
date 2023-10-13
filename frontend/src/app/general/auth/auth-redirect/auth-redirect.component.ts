/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth/auth.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-auth-redirect',
  templateUrl: './auth-redirect.component.html',
  styleUrls: ['./auth-redirect.component.css'],
})
export class AuthRedirectComponent implements OnInit {
  constructor(
    private route: ActivatedRoute,
    private authService: AuthService,
    private userService: UserService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      if (params.error) {
        const redirect_url =
          '/auth?' +
          Object.keys(params)
            .map((key) =>
              ['error', 'error_description', 'error_uri'].includes(key)
                ? [key, params[key]].join('=')
                : '',
            )
            .join('&');
        this.router.navigateByUrl(redirect_url);
        return;
      }
      this.authService
        .getAccessToken(params.code, params.state)
        .subscribe((res) => {
          this.authService.logIn(res.access_token, res.refresh_token);
          this.userService.updateOwnUser();

          this.router.navigateByUrl(this.authService.getCurrentPath());
        });
    });
  }
}
