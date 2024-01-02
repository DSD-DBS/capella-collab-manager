/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { AuthService } from 'src/app/services/auth/auth.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-nav-bar-menu',
  templateUrl: './nav-bar-menu.component.html',
  styleUrls: ['./nav-bar-menu.component.css'],
})
export class NavBarMenuComponent {
  constructor(
    public authService: AuthService,
    public navBarService: NavBarService,
    public userService: UserService,
  ) {}
}
