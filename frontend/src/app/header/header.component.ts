/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit, Renderer2 } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { LocalStorageService } from '../auth/local-storage/local-storage.service';
import { ReleaseNotesComponent } from '../metadata/release-notes/release-notes.component';
import { AuthService } from '../services/auth/auth.service';
import { RepositoryService } from '../services/repository/repository.service';
import { UserService } from '../services/user/user.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent implements OnInit {
  @Input()
  title = 'Capella Collaboration Plattform';

  constructor(
    public localStorageService: LocalStorageService,
    public authService: AuthService,
    public userService: UserService,
    public repositoryService: RepositoryService,
    public dialog: MatDialog
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

  openReleaseNotes(): void {
    this.dialog.open(ReleaseNotesComponent);
  }
}
