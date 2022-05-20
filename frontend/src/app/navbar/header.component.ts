// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Input, OnInit } from '@angular/core';
import { LocalStorageService } from '../auth/local-storage/local-storage.service';
import { AuthService } from '../services/auth/auth.service';
import { ProjectService } from '../projects/service/project.service';
import { UserService } from '../services/user/user.service';
import { NavBarService } from './service/nav-bar.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent implements OnInit {
  constructor(
    public localStorageService: LocalStorageService,
    public authService: AuthService,
    public userService: UserService,
    public projectService: ProjectService,
    public navbarService: NavBarService
  ) {}

  ngOnInit(): void {
    this.createGithubButton();
  }

  createGithubButton(): void {
    let githubButtonScript = document.createElement('script');
    githubButtonScript.type = 'text/javascript';
    githubButtonScript.src = 'https://buttons.github.io/buttons.js';
    document.head.appendChild(githubButtonScript);
  }
}
