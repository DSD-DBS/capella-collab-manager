/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgIf, NgClass } from '@angular/common';
import { Component, Input } from '@angular/core';
import { ViewerSession } from '../session-viewer.service';

@Component({
  selector: 'app-session-iframe',
  templateUrl: './session-iframe.component.html',
  styleUrls: ['./session-iframe.component.css'],
  standalone: true,
  imports: [NgIf, NgClass],
})
export class SessionIFrameComponent {
  @Input({ required: true }) session!: ViewerSession;
}
