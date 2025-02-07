/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, NgClass } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { MatButton, MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { DOCS_URL } from 'src/app/environment';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { PageLayoutService } from 'src/app/page-layout/page-layout.service';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { NavBarService } from '../../nav-bar/nav-bar.service';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  imports: [MatButton, AsyncPipe, MatIconModule, MatButtonModule, NgClass],
})
export class AuthComponent implements OnInit {
  public params = {} as Params;
  public metadataService = inject(MetadataService);
  public authService = inject(AuthenticationWrapperService);
  public navBarService = inject(NavBarService);
  private pageLayoutService = inject(PageLayoutService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private dialog = inject(MatDialog);

  constructor() {
    this.pageLayoutService.hideNavbar();
    if (this.router.url.startsWith('/logout')) {
      this.authService.logOut();
      this.dialog.closeAll();
    }
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.params = params;
      if (params.reason && params.reason === 'session-expired') {
        this.authService.login();
      }
    });
  }

  getDocsURL(): string {
    return DOCS_URL + '/';
  }
}
