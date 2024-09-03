/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgFor } from '@angular/common';
import { Component, ViewEncapsulation } from '@angular/core';
import { NoticeService } from '../../services/notice/notice.service';

@Component({
  selector: 'app-notice',
  templateUrl: './notice.component.html',
  styleUrls: ['./notice.component.css'],
  encapsulation: ViewEncapsulation.None,
  standalone: true,
  imports: [NgFor],
})
export class NoticeComponent {
  constructor(public noticeService: NoticeService) {}
}
