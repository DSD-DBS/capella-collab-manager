// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth/auth.service';
import { RepositoryService } from 'src/app/services/repository/repository.service';
import { UserService } from 'src/app/services/user/user.service';
import { LocalStorageService } from '../local-storage/local-storage.service';
import { CookieService } from 'ngx-cookie';

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
    private localStorageService: LocalStorageService,
    private router: Router,
    private repositoryService: RepositoryService,
    private cookieService: CookieService
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      if (params['error']) {
        const test = Object.keys(params).map(key => {
          key
        })
        const redirect_url = '/auth?' + Object.keys(params).map(key => 
          ['error', 'error_description', 'error_uri'].includes(key) ? [key, params[key]].join('=') : ""
        ).join('&')
        this.router.navigateByUrl(redirect_url)
        return
      }
      this.authService
        .getAccessToken(params['code'], params['state'])
        .subscribe((res) => {
          this.localStorageService.setValue('access_token', res.access_token);
          this.localStorageService.setValue('refresh_token', res.refresh_token);

          this.cookieService.put('access_token', res.access_token, {
            path: '/prometheus',
          });

          this.userService.getAndSaveOwnUser();
          this.repositoryService.getAndSaveManagerRole();

          this.router.navigateByUrl('/');
        });
    });
  }
}
