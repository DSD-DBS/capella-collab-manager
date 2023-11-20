/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { EventsService, HistoryEvent } from './service/events.service';

@Component({
  selector: 'app-events',
  templateUrl: './events.component.html',
  styleUrls: ['./events.component.css'],
})
export class EventsComponent implements OnInit, AfterViewInit {
  @ViewChild(MatPaginator) paginator: MatPaginator | null = null;
  @ViewChild(MatSort) sort: MatSort | null = null;

  displayedColumns: string[] = [
    'eventType',
    'userName',
    'executorName',
    'executionTime',
    'projectName',
    'reason',
  ];

  historyEventData: HistoryEvent[] = [];
  historyEventDataSource = new MatTableDataSource<HistoryEvent>(
    this.historyEventData,
  );

  constructor(private eventService: EventsService) {}

  ngOnInit(): void {
    this.eventService.historyEvents.subscribe((historyEvents) => {
      this.historyEventData = historyEvents;
      this.historyEventDataSource.data = this.historyEventData;
    });
    this.eventService.loadHistoryEvents();
  }

  ngAfterViewInit(): void {
    this.historyEventDataSource.paginator = this.paginator;
    this.historyEventDataSource.sortingDataAccessor =
      this.eventService.customSortingDataAccessor;
    this.historyEventDataSource.sort = this.sort;
  }
}
