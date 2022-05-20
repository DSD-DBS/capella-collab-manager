// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';

@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css'],
})
export class LogoutComponent implements OnInit {
  reason = '';
  autoLogin = false;

  constructor(
    private route: ActivatedRoute,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Logout';
    this.navbarService.disableAll();
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.reason = params['reason'];
      if (this.reason === 'session-expired') {
        this.autoLogin = true;
      }
    });
  }
}
