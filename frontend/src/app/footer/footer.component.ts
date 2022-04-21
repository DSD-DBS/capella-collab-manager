// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { TermsConditionsComponent } from './terms-conditions/terms-conditions.component';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css'],
})
export class FooterComponent implements OnInit {
  constructor(public dialog: MatDialog) {}

  ngOnInit(): void {}

  openTC(): void {
    this.dialog.open(TermsConditionsComponent);
  }
}
