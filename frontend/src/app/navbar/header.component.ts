/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { ProjectService } from 'src/app/services/project/project.service';
import { LocalStorageService } from '../auth/local-storage/local-storage.service';
import { AuthService } from '../services/auth/auth.service';
import { UserService } from '../services/user/user.service';
import { NavBarService } from './service/nav-bar.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent implements OnInit {
  numMessages: number = 0;

  constructor(
    public localStorageService: LocalStorageService,
    public authService: AuthService,
    public userService: UserService,
    public projectService: ProjectService,
    public navbarService: NavBarService
  ) {}

  ngOnInit(): void {
    this.createGithubButton();
    this.collectRequests();
  }

  collectRequests() {
    this.projectService.listStagedProjects().subscribe((stagedProjects) => {
      this.numMessages += stagedProjects.length;
    });
  }

  createGithubButton(): void {
    let githubButtonScript = document.createElement('script');
    githubButtonScript.type = 'text/javascript';
    githubButtonScript.src = 'https://buttons.github.io/buttons.js';
    document.head.appendChild(githubButtonScript);
  }
}
