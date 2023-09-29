/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MetadataService } from 'src/app/general/metadata/metadata.service';

@Component({
  selector: 'app-legal',
  templateUrl: './legal.component.html',
  styleUrls: ['./legal.component.css'],
})
export class LegalComponent {
  constructor(public metadataService: MetadataService) {}
}
