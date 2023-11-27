/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';
import { ViewerSession } from '../session-viewer.service';

@Component({
  selector: 'app-session-iframe',
  templateUrl: './session-iframe.component.html',
  styleUrls: ['./session-iframe.component.css'],
})
export class SessionIFrameComponent {
  @Input({ required: true }) session!: ViewerSession;
}
