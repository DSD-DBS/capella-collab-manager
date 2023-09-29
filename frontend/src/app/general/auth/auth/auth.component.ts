/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { PageLayoutService } from 'src/app/page-layout/page-layout.service';
import { AuthService } from 'src/app/services/auth/auth.service';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css'],
})
export class AuthComponent implements OnInit {
  @Input()
  set autoLogin(value: boolean) {
    if (value) {
      this.authService.webSSO();
    }
  }

  public params = {} as ParamMap;

  constructor(
    public metadataService: MetadataService,
    private authService: AuthService,
    private pageLayoutService: PageLayoutService,
    private route: ActivatedRoute
  ) {
    this.pageLayoutService.disableAll();
  }

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((res) => {
      this.params = res;
    });
  }

  webSSO() {
    this.authService.webSSO();
  }
}
