/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { Session } from '../../schemes';
import { OwnSessionService } from '../../services/own-session/own-session.service';
import { SessionService } from '../../services/session/session.service';

@Component({
  selector: 'app-session-created',
  templateUrl: './session-created.component.html',
  styleUrls: ['./session-created.component.css'],
})
export class SessionCreatedComponent implements OnInit {
  @Input()
  session: Session | undefined = undefined;
  constructor(private ownSessionService: OwnSessionService) {}

  ngOnInit(): void {
    this.ownSessionService.refreshSessions().subscribe();
  }
}
