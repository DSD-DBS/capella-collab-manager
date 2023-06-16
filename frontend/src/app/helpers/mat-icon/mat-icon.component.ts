/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-mat-icon',
  templateUrl: './mat-icon.component.html',
  styleUrls: ['./mat-icon.component.css'],
})
export class MatIconComponent implements OnInit {
  @Input() position: MatIconPosition = null;
  @Input() size = '24px';

  style = {};

  ngOnInit(): void {
    this.style = {
      width: this.size,
      height: this.size,
      'font-size': this.size,
      position: 'relative',
      'margin-right': '0px',
    };
  }
}

type MatIconPosition = 'right' | 'left' | null;
