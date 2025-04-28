/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { DatePipe } from '@angular/common';
import {
  AfterViewInit,
  Component,
  OnInit,
  ViewChild,
  inject,
} from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
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
import { EventsService, HistoryEvent } from 'src/app/openapi';

@Component({
  selector: 'app-events',
  templateUrl: './events.component.html',
  imports: [
    MatTable,
    MatSort,
    MatColumnDef,
    MatHeaderCellDef,
    MatHeaderCell,
    MatSortHeader,
    MatCellDef,
    MatCell,
    MatHeaderRowDef,
    MatHeaderRow,
    MatRowDef,
    MatRow,
    MatPaginator,
    DatePipe,
  ],
})
export class EventsComponent implements OnInit, AfterViewInit {
  private eventService = inject(EventsService);

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

  ngOnInit(): void {
    this.eventService.getEvents().subscribe((historyEvents) => {
      this.historyEventData = historyEvents;
      this.historyEventDataSource.data = this.historyEventData;
    });
  }

  ngAfterViewInit(): void {
    this.historyEventDataSource.paginator = this.paginator;
    this.historyEventDataSource.sortingDataAccessor =
      this.customSortingDataAccessor;
    this.historyEventDataSource.sort = this.sort;
  }

  customSortingDataAccessor(data: HistoryEvent, sortHeaderId: string): string {
    switch (sortHeaderId) {
      case 'eventType':
        return data.event_type;
      case 'userName':
        return data.user.name;
      case 'executorName':
        return data.executor ? data.executor.name : 'System';
      case 'executionTime':
        return data.execution_time;
      case 'projectName':
        return data.project ? data.project.name : '';
      case 'reason':
        return data.reason ?? '';
      default:
        return '';
    }
  }
}
