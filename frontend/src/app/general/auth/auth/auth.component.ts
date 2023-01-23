/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import { AuthService } from 'src/app/services/auth/auth.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css'],
})
export class AuthComponent implements OnInit {
  @Input()
  set autoLogin(value: boolean) {
    if (value) {
      this.authService.webSSO();
    }
  }

  authProvider = environment.authentication;
  public params = {} as ParamMap;

  constructor(
    private authService: AuthService,
    private navbarService: NavBarService,
    private route: ActivatedRoute
  ) {
    this.navbarService.disableAll();
  }

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((res) => {
      this.params = res;
    });
  }

  webSSO() {
    this.authService.webSSO();
  }
}
