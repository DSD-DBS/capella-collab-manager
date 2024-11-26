/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatDivider } from '@angular/material/divider';
import { MatIcon } from '@angular/material/icon';
import { MatList, MatListItem } from '@angular/material/list';
import { RouterLink } from '@angular/router';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-nav-bar-menu',
  templateUrl: './nav-bar-menu.component.html',
  styleUrls: ['./nav-bar-menu.component.css'],
  imports: [MatList, MatListItem, MatIcon, RouterLink, MatDivider, AsyncPipe],
})
export class NavBarMenuComponent {
  constructor(
    public authService: AuthenticationWrapperService,
    public navBarService: NavBarService,
    public userService: OwnUserWrapperService,
  ) {}
}
