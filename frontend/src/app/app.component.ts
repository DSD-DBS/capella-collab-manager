/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgClass, AsyncPipe } from '@angular/common';
import { AfterViewInit, Component, ViewChild } from '@angular/core';
import {
  MatSidenav,
  MatDrawerContainer,
  MatDrawer,
  MatDrawerContent,
} from '@angular/material/sidenav';
import { RouterOutlet } from '@angular/router';
import slugify from 'slugify';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { FooterComponent } from './general/footer/footer.component';
import { HeaderComponent } from './general/header/header.component';
import { NavBarMenuComponent } from './general/nav-bar-menu/nav-bar-menu.component';
import { NoticeComponent } from './general/notice/notice.component';
import { PageLayoutService } from './page-layout/page-layout.service';
import { FullscreenService } from './sessions/service/fullscreen.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [
    MatDrawerContainer,
    MatDrawer,
    NavBarMenuComponent,
    MatDrawerContent,
    NgIf,
    HeaderComponent,
    NgClass,
    NoticeComponent,
    RouterOutlet,
    FooterComponent,
    AsyncPipe,
  ],
})
export class AppComponent implements AfterViewInit {
  constructor(
    public pageLayoutService: PageLayoutService,
    public fullscreenService: FullscreenService,
    private navBarService: NavBarService,
  ) {
    slugify.extend({ '.': '-' });
  }

  @ViewChild('sidenav') private sidenav?: MatSidenav;

  ngAfterViewInit(): void {
    this.navBarService.sidenav = this.sidenav;
  }
}
