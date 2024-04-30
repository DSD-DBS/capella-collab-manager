/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MetadataService } from 'src/app/general/metadata/metadata.service';

@Component({
  selector: 'app-legal',
  templateUrl: './legal.component.html',
  styleUrls: ['./legal.component.css'],
  standalone: true,
  imports: [AsyncPipe],
})
export class LegalComponent {
  constructor(public metadataService: MetadataService) {}
}
