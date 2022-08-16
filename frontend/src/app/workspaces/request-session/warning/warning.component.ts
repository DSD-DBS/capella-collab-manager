// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-warning',
  templateUrl: './warning.component.html',
  styleUrls: ['./warning.component.css'],
})
export class WarningComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {}

  @Input()
  persistent = true;

  @Input()
  warning = '';
}
