/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { PageLayoutService } from './page-layout/page-layout.service';
import { FullscreenService } from './sessions/service/fullscreen.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements AfterViewInit {
  constructor(
    public pageLayoutService: PageLayoutService,
    public fullscreenService: FullscreenService,
    private navBarService: NavBarService
  ) {}

  @ViewChild('sidenav') private sidenav?: MatSidenav;

  ngAfterViewInit(): void {
    this.navBarService.sidenav = this.sidenav;
  }
}
