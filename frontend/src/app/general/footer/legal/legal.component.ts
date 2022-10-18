/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-legal',
  templateUrl: './legal.component.html',
  styleUrls: ['./legal.component.css'],
})
export class LegalComponent {
  imprint = environment.imprint;
  privacy = environment.privacy;

  constructor() {}
}
