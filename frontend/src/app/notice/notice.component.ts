/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { NoticeService } from '../services/notice/notice.service';

@Component({
  selector: 'app-notice',
  templateUrl: './notice.component.html',
  styleUrls: ['./notice.component.css'],
  encapsulation: ViewEncapsulation.None,
})
export class NoticeComponent implements OnInit {
  constructor(public noticeService: NoticeService) {}

  ngOnInit(): void {}
}
