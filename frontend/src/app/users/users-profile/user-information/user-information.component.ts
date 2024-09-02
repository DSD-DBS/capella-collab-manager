/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  Input,
  ViewChild,
} from '@angular/core';
import { MatDividerModule } from '@angular/material/divider';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { HistoryEvent, User, UsersService } from 'src/app/openapi';
import { UserWrapperService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-user-information',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    NgxSkeletonLoaderModule,
    MatPaginator,
    MatDividerModule,
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
export class UserInformationComponent implements AfterViewInit {
  _user: User | undefined;

  @Input()
  set user(value: User | undefined) {
    this._user = value;
    if (value && this.userService.user?.role === 'administrator') {
      this.usersService.getUserEvents(value.id).subscribe({
        next: (userEvents) => {
          this.userEvents = userEvents;
          this.historyEventDataSource.data = userEvents;
          this.historyEventDataSource.paginator = this.paginator;
        },
      });
    }
  }

  get user(): User | undefined {
    return this._user;
  }

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

  constructor(
    public userService: UserWrapperService,
    private usersService: UsersService,
  ) {}
}
