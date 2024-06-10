/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MatIconButton, MatAnchor, MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatMenu, MatMenuItem, MatMenuTrigger } from '@angular/material/menu';
import { RouterLink } from '@angular/router';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { AuthService } from '../../services/auth/auth.service';
import { UserWrapperService } from '../../services/user/user.service';
import { BreadcrumbsComponent } from '../breadcrumbs/breadcrumbs.component';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  standalone: true,
  imports: [
    MatIconButton,
    MatIcon,
    MatAnchor,
    RouterLink,
    MatMenu,
    MatMenuItem,
    MatButton,
    MatMenuTrigger,
    BreadcrumbsComponent,
  ],
})
export class HeaderComponent {
  constructor(
    public authService: AuthService,
    public userService: UserWrapperService,
    public navBarService: NavBarService,
  ) {}
}
