/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth/auth.service';

@Component({
  selector: 'app-logout-redirect',
  templateUrl: './logout-redirect.component.html',
  styleUrls: ['./logout-redirect.component.css'],
  standalone: true,
})
export class LogoutRedirectComponent implements OnInit {
  constructor(
    private authService: AuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.authService.logOut();
    this.router.navigate(['/logout'], { queryParamsHandling: 'merge' });
  }
}
