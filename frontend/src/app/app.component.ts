/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
import { AfterViewInit, Component, ViewChild, inject } from '@angular/core';
import {
  MatSidenav,
  MatDrawerContainer,
  MatDrawer,
  MatDrawerContent,
} from '@angular/material/sidenav';
import { RouterOutlet } from '@angular/router';
import slugify from 'slugify';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { AnnouncementListComponent } from './general/announcement/announcement-list.component';
import { FooterComponent } from './general/footer/footer.component';
import { HeaderComponent } from './general/header/header.component';
import { NavBarMenuComponent } from './general/nav-bar-menu/nav-bar-menu.component';
import { PageLayoutService } from './page-layout/page-layout.service';
import { FeedbackWrapperService } from './sessions/feedback/feedback.service';
import { FullscreenService } from './sessions/service/fullscreen.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  imports: [
    MatDrawerContainer,
    MatDrawer,
    NavBarMenuComponent,
    MatDrawerContent,
    HeaderComponent,
    NgClass,
    AnnouncementListComponent,
    RouterOutlet,
    FooterComponent,
    AsyncPipe,
  ],
})
export class AppComponent implements AfterViewInit {
  pageLayoutService = inject(PageLayoutService);
  fullscreenService = inject(FullscreenService);
  private navBarService = inject(NavBarService);
  private feedbackService = inject(FeedbackWrapperService);

  constructor() {
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
