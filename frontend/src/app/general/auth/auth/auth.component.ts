/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatButton, MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { PageLayoutService } from 'src/app/page-layout/page-layout.service';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { environment } from 'src/environments/environment';
import { WelcomeComponent } from '../../welcome/welcome.component';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  standalone: true,
  imports: [
    MatButton,
    AsyncPipe,
    WelcomeComponent,
    MatIconModule,
    MatButtonModule,
  ],
})
export class AuthComponent implements OnInit {
  reason = '';

  public params = {} as ParamMap;

  constructor(
    public metadataService: MetadataService,
    public authService: AuthenticationWrapperService,
    private pageLayoutService: PageLayoutService,
    private route: ActivatedRoute,
  ) {
    this.pageLayoutService.hideNavbar();
    this.route.queryParams.subscribe((params) => {
      this.reason = params.reason;
      if (this.reason === 'session-expired') {
        this.login();
      }
    });
  }

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((res) => {
      this.params = res;
    });
  }

  getDocsURL(): string {
    return environment.docs_url + '/';
  }

  login(): void {
    this.authService.login('/');
  }
}
