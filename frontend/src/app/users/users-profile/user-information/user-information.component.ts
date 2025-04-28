/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  OnInit,
  ViewChild,
  inject,
} from '@angular/core';
import { MatDividerModule } from '@angular/material/divider';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { of, switchMap } from 'rxjs';
import { HistoryEvent, UsersService } from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';
import { RelativeTimeComponent } from '../../../general/relative-time/relative-time.component';

@Component({
  selector: 'app-user-information',
  imports: [
    CommonModule,
    MatTableModule,
    NgxSkeletonLoaderModule,
    MatPaginator,
    MatDividerModule,
    RelativeTimeComponent,
  ],
  styles: `
    .mat-cell,
    .mat-header-cell {
      padding: 8px 8px 8px 0;
    }
  `,
  templateUrl: './user-information.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserInformationComponent implements OnInit, AfterViewInit {
  userService = inject(OwnUserWrapperService);
  userWrapperService = inject(UserWrapperService);
  private usersService = inject(UsersService);

  userEvents?: HistoryEvent[];

  @ViewChild(MatPaginator) paginator: MatPaginator | null = null;
  displayedColumns: string[] = [
    'eventType',
    'executorName',
    'executionTime',
    'projectName',
    'reason',
  ];

  historyEventDataSource = new MatTableDataSource<HistoryEvent>(undefined);

  ngAfterViewInit(): void {
    this.historyEventDataSource.paginator = this.paginator;
  }

  ngOnInit(): void {
    this.userWrapperService.user$
      .pipe(
        switchMap((user) => {
          if (!user) return of(undefined);
          return this.usersService.getUserEvents(user.id);
        }),
      )
      .subscribe({
        next: (userEvents) => {
          this.userEvents = userEvents;
          if (userEvents) {
            this.historyEventDataSource.data = userEvents;
          }
          this.historyEventDataSource.paginator = this.paginator;
        },
      });
  }
}
