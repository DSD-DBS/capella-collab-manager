/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgFor, AsyncPipe, DatePipe } from '@angular/common';
import {
  AfterViewInit,
  Component,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import { MatDivider } from '@angular/material/divider';
import { MatPaginator } from '@angular/material/paginator';
import {
  MatTableDataSource,
  MatTable,
  MatColumnDef,
  MatHeaderCellDef,
  MatHeaderCell,
  MatCellDef,
  MatCell,
  MatHeaderRowDef,
  MatHeaderRow,
  MatRowDef,
  MatRow,
} from '@angular/material/table';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { BehaviorSubject, filter, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { HistoryEvent, Project, User, UsersService } from 'src/app/openapi';
import { UserWrapperService } from 'src/app/services/user/user.service';

@UntilDestroy()
@Component({
  selector: 'app-users-profile',
  templateUrl: './users-profile.component.html',
  styleUrls: ['./users-profile.component.css'],
  standalone: true,
  imports: [
    NgIf,
    MatTable,
    MatColumnDef,
    MatHeaderCellDef,
    MatHeaderCell,
    MatCellDef,
    MatCell,
    MatHeaderRowDef,
    MatHeaderRow,
    MatRowDef,
    MatRow,
    NgxSkeletonLoaderModule,
    MatPaginator,
    MatDivider,
    NgFor,
    RouterLink,
    AsyncPipe,
    DatePipe,
  ],
})
export class UsersProfileComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild(MatPaginator) paginator: MatPaginator | null = null;
  displayedColumns: string[] = [
    'eventType',
    'executorName',
    'executionTime',
    'projectName',
    'reason',
  ];

  user: User | undefined;
  commonProjects = new BehaviorSubject<Project[] | undefined>(undefined);
  userEvents?: HistoryEvent[];

  historyEventDataSource = new MatTableDataSource<HistoryEvent>([]);

  public readonly commonProjects$ = this.commonProjects.asObservable();

  constructor(
    public userService: UserWrapperService,
    private usersService: UsersService,
    private route: ActivatedRoute,
    private breadcrumbsService: BreadcrumbsService,
  ) {}

  ngOnInit() {
    this.route.params
      .pipe(
        filter((params) => params['userId']),
        map((params) => params['userId']),
      )
      .subscribe((userId: number) => {
        this.usersService.getUser(userId).subscribe((user) => {
          this.user = user;
          this.breadcrumbsService.updatePlaceholder({ user: user });
          if (userId !== this.userService.user?.id) {
            this.usersService.getCommonProjects(userId).subscribe({
              next: (projects) => this.commonProjects.next(projects),
              error: () => this.commonProjects.next(undefined),
            });
          }

          if (this.userService.user?.role === 'administrator') {
            this.usersService.getUserEvents(userId).subscribe({
              next: (userEvents) => {
                this.userEvents = userEvents;
                this.historyEventDataSource.data = userEvents;
                this.historyEventDataSource.paginator = this.paginator;
              },
            });
          }
        });
      });
  }

  ngAfterViewInit(): void {
    this.historyEventDataSource.paginator = this.paginator;
  }

  ngOnDestroy(): void {
    this.breadcrumbsService.updatePlaceholder({ user: undefined });
  }
}
