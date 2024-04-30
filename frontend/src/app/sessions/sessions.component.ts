/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { ActiveSessionsComponent } from './user-sessions-wrapper/active-sessions/active-sessions.component';
import { CreatePersistentSessionComponent } from './user-sessions-wrapper/create-sessions/create-persistent-session/create-persistent-session.component';
import { UserSessionsWrapperComponent } from './user-sessions-wrapper/user-sessions-wrapper.component';

@Component({
  selector: 'app-sesssions',
  templateUrl: './sessions.component.html',
  standalone: true,
  imports: [
    UserSessionsWrapperComponent,
    CreatePersistentSessionComponent,
    ActiveSessionsComponent,
  ],
})
export class SessionsComponent {}
