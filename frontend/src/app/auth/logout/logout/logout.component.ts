// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css'],
})
export class LogoutComponent implements OnInit {
  reason = '';
  autoLogin = false;

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.reason = params['reason'];
      if (this.reason === 'session-expired') {
        this.autoLogin = true;
      }
    });
  }
}
