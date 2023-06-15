/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, HostListener, OnInit } from '@angular/core';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { AuthService } from '../../services/auth/auth.service';
import { UserService } from '../../services/user/user.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent {
  constructor(
    public authService: AuthService,
    public userService: UserService,
    public navBarService: NavBarService
  ) {}

  isSmallScreen = false;

  ngOnInit(): void {
    this.createGithubButton();
    this.updateScreenSize();
  }

  createGithubButton(): void {
    const githubButtonScript = document.createElement('script');
    githubButtonScript.type = 'text/javascript';
    githubButtonScript.src = 'https://buttons.github.io/buttons.js';
    document.head.appendChild(githubButtonScript);
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    this.updateScreenSize();
  }

  updateScreenSize() {
    this.isSmallScreen = window.innerWidth < 1300;
  }
}
