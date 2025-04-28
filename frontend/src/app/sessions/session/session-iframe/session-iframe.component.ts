/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, NgClass } from '@angular/common';
import { Component, inject, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { FullscreenService } from 'src/app/sessions/service/fullscreen.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { ViewerSession } from '../session-viewer.service';

@Component({
  selector: 'app-session-iframe',
  templateUrl: './session-iframe.component.html',
  styleUrls: ['./session-iframe.component.css'],
  imports: [NgClass, MatIconModule, AsyncPipe],
})
export class SessionIFrameComponent {
  sessionService = inject(SessionService);

  @Input({ required: true }) session!: ViewerSession;

  public fullscreenService = inject(FullscreenService);
}
