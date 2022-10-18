/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-session-progress-icon',
  templateUrl: './session-progress-icon.component.html',
  styleUrls: ['./session-progress-icon.component.css'],
})
export class SessionProgressIconComponent {
  @Input()
  state = 'pending';

  constructor() {}
}
