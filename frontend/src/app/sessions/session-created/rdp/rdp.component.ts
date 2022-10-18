/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';
import { Session } from 'src/app/schemes';

@Component({
  selector: 'app-rdp',
  templateUrl: './rdp.component.html',
  styleUrls: ['./rdp.component.css'],
})
export class RDPComponent {
  @Input()
  session: Session | undefined = undefined;

  constructor() {}
}
