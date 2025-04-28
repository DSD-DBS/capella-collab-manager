/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
  inject,
} from '@angular/core';
import { ActivatedRoute, RouterOutlet } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { User } from 'src/app/openapi';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';

@UntilDestroy()
@Component({
  selector: 'app-user-wrapper',
  imports: [CommonModule, RouterOutlet],
  template: `<router-outlet></router-outlet>`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserWrapperComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  userWrapperService = inject(UserWrapperService);
  private breadcrumbsService = inject(BreadcrumbsService);

  ngOnInit() {
    this.updateUserOnRouteUpdate();
    this.updateBreadcrumb();
  }

  ngOnDestroy(): void {
    this.userWrapperService.resetUser();
    this.breadcrumbsService.updatePlaceholder({ user: undefined });
  }

  updateUserOnRouteUpdate() {
    this.route.params
      .pipe(
        map((params) => params.user),
        untilDestroyed(this),
      )
      .subscribe((userID: string) => {
        this.userWrapperService.loadUser(parseInt(userID));
      });
  }

  updateBreadcrumb() {
    this.userWrapperService.user$
      .pipe(untilDestroyed(this))
      .subscribe((user: User | undefined) =>
        this.breadcrumbsService.updatePlaceholder({ user }),
      );
  }
}
