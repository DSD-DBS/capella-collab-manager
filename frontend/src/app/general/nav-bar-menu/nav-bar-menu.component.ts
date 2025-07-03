/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatDivider } from '@angular/material/divider';
import { MatIcon } from '@angular/material/icon';
import { MatList, MatListItem } from '@angular/material/list';
import { RouterLink } from '@angular/router';
import { LogoComponent } from 'src/app/general/logo/logo.component';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { ThemeToggleComponent } from '../theme-toggle/theme-toggle.component';

@Component({
  selector: 'app-nav-bar-menu',
  templateUrl: './nav-bar-menu.component.html',
  imports: [
    MatList,
    MatListItem,
    MatIcon,
    RouterLink,
    MatDivider,
    AsyncPipe,
    LogoComponent,
    ThemeToggleComponent,
  ],
})
export class NavBarMenuComponent {
  authService = inject(AuthenticationWrapperService);
  navBarService = inject(NavBarService);
  userService = inject(OwnUserWrapperService);
}
