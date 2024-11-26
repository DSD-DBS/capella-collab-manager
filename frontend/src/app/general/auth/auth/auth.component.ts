/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatButton, MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { PageLayoutService } from 'src/app/page-layout/page-layout.service';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { environment } from 'src/environments/environment';
import { WelcomeComponent } from '../../welcome/welcome.component';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  imports: [
    MatButton,
    AsyncPipe,
    WelcomeComponent,
    MatIconModule,
    MatButtonModule,
  ],
})
export class AuthComponent implements OnInit {
  public params = {} as Params;

  constructor(
    public metadataService: MetadataService,
    public authService: AuthenticationWrapperService,
    private pageLayoutService: PageLayoutService,
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog,
  ) {
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
    return environment.docs_url + '/';
  }
}
