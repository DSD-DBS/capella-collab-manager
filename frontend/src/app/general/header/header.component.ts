/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatIconButton, MatAnchor, MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatMenu, MatMenuItem, MatMenuTrigger } from '@angular/material/menu';
import { RouterLink } from '@angular/router';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { AuthenticationWrapperService } from '../../services/auth/auth.service';
import { OwnUserWrapperService } from '../../services/user/user.service';
import { BreadcrumbsComponent } from '../breadcrumbs/breadcrumbs.component';
import { LogoComponent } from '../logo/logo.component';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
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
    AsyncPipe,
    LogoComponent,
  ],
})
export class HeaderComponent {
  constructor(
    public authService: AuthenticationWrapperService,
    public userService: OwnUserWrapperService,
    public navBarService: NavBarService,
  ) {}
}
