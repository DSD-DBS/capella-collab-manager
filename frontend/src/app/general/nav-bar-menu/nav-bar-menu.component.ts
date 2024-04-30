/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgFor, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { MatDivider } from '@angular/material/divider';
import { MatIcon } from '@angular/material/icon';
import { MatList, MatListItem } from '@angular/material/list';
import { RouterLink } from '@angular/router';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { AuthService } from 'src/app/services/auth/auth.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-nav-bar-menu',
  templateUrl: './nav-bar-menu.component.html',
  styleUrls: ['./nav-bar-menu.component.css'],
  standalone: true,
  imports: [MatList, NgFor, NgIf, MatListItem, MatIcon, RouterLink, MatDivider],
})
export class NavBarMenuComponent {
  constructor(
    public authService: AuthService,
    public navBarService: NavBarService,
    public userService: UserService,
  ) {}
}
