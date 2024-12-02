/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
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
import { FeedbackWrapperService } from './sessions/feedback/feedback.service';
import { FullscreenService } from './sessions/service/fullscreen.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [
    MatDrawerContainer,
    MatDrawer,
    NavBarMenuComponent,
    MatDrawerContent,
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
    private feedbackService: FeedbackWrapperService,
  ) {
    slugify.extend({ '.': '-' });
  }

  @ViewChild('sidenav') private sidenav?: MatSidenav;

  ngAfterViewInit(): void {
    this.navBarService.sidenav = this.sidenav;
  }

  constructMinHeight(): string {
    let stmt = 'calc(100vh - 16px'; // Subtract margin of body
    if (this.pageLayoutService.showNavbar) {
      stmt += ' - 100px';
    }
    if (this.pageLayoutService.showFooter) {
      stmt += ' - 115px - 8px';
    }
    stmt += ')';
    return stmt;
  }
}
