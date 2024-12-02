/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass } from '@angular/common';
import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { SessionService } from 'src/app/sessions/service/session.service';
import { ViewerSession } from '../session-viewer.service';

@Component({
  selector: 'app-session-iframe',
  templateUrl: './session-iframe.component.html',
  styleUrls: ['./session-iframe.component.css'],
  imports: [NgClass, MatIconModule],
})
export class SessionIFrameComponent {
  @Input({ required: true }) session!: ViewerSession;

  constructor(public sessionService: SessionService) {}
}
