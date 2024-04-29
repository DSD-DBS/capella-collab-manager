/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { PageLayoutService } from 'src/app/page-layout/page-layout.service';
import { AuthComponent } from '../../auth/auth.component';

@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css'],
  standalone: true,
  imports: [NgIf, AuthComponent],
})
export class LogoutComponent implements OnInit {
  reason = '';
  autoLogin = false;

  constructor(
    private route: ActivatedRoute,
    private pageLayoutService: PageLayoutService,
  ) {
    this.pageLayoutService.disableAll();
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.reason = params.reason;
      if (this.reason === 'session-expired') {
        this.autoLogin = true;
      }
    });
  }
}
