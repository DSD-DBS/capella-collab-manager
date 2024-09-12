/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, NgClass } from '@angular/common';
import { Component, ViewEncapsulation } from '@angular/core';
import { NoticeWrapperService } from 'src/app/general/notice/notice.service';

@Component({
  selector: 'app-notice',
  templateUrl: './notice.component.html',
  styleUrls: ['./notice.component.css'],
  encapsulation: ViewEncapsulation.None,
  standalone: true,
  imports: [NgClass, AsyncPipe],
})
export class NoticeComponent {
  constructor(public noticesWrapperService: NoticeWrapperService) {}
}
