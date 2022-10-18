/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { environment } from 'src/environments/environment';
import { TermsConditionsComponent } from './terms-conditions/terms-conditions.component';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css'],
})
export class FooterComponent {
  constructor(public dialog: MatDialog) {}

  provider = environment.provider;

  openTC(): void {
    this.dialog.open(TermsConditionsComponent);
  }
}
