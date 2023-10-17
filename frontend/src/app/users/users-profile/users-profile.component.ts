/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  AfterViewInit,
  Component,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { BehaviorSubject, filter, map } from 'rxjs';
import { HistoryEvent } from 'src/app/events/service/events.service';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { Project } from 'src/app/projects/service/project.service';
import {
  User,
  UserHistory,
  UserService,
} from 'src/app/services/user/user.service';

@UntilDestroy()
@Component({
  selector: 'app-users-profile',
  templateUrl: './users-profile.component.html',
  styleUrls: ['./users-profile.component.css'],
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
  userId: number | undefined;
  commonProjects = new BehaviorSubject<Project[] | undefined>(undefined);
  joinedString: string | undefined;
  userHistory?: UserHistory;

  historyEventDataSource = new MatTableDataSource<HistoryEvent>([]);

  public readonly commonProjects$ = this.commonProjects.asObservable();

  constructor(
    public userService: UserService,
    private route: ActivatedRoute,
    private breadcrumbsService: BreadcrumbsService,
  ) {}

  ngOnInit() {
    this.userService.updateOwnUser();
    this.route.params
      .pipe(
        filter((params) => params['userId']),
        map((params) => params['userId']),
      )
      .subscribe((userId: number) => {
        this.userId = +userId;
        if (this.userId) {
          this.userService.getUserById(this.userId).subscribe((user) => {
            this.user = user;
            this.breadcrumbsService.updatePlaceholder({ user: user });
            if (this.userId !== this.userService.user?.id) {
              this.userService.loadCommonProjects(this.userId!).subscribe({
                next: (projects) => this.commonProjects.next(projects),
                error: () => this.commonProjects.next(undefined),
              });
            }
            this.userService
              .getUserHistory(this.userId!)
              .subscribe((history) => {
                if (history.created) {
                  this.joinedString = `Joined the collaboration manager in ${new Date(
                    history.created,
                  )
                    ?.getFullYear()
                    ?.toString()}`;
                } else {
                  this.joinedString = '';
                }
              });
          });
        }
      });
    if (this.userService.user?.role === 'administrator') {
      this.userService.getUserHistory(this.userService.user?.id).subscribe({
        next: (userHistory) => {
          this.userHistory = userHistory;
          this.historyEventDataSource.data = userHistory.events;
          this.historyEventDataSource.paginator = this.paginator;
        },
      });
    }
  }

  ngAfterViewInit(): void {
    this.historyEventDataSource.paginator = this.paginator;
  }

  ngOnDestroy(): void {
    this.breadcrumbsService.updatePlaceholder({ user: undefined });
  }
}
