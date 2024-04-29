/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgClass } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { MatIcon } from '@angular/material/icon';

@Component({
  selector: 'app-mat-icon',
  templateUrl: './mat-icon.component.html',
  styleUrls: ['./mat-icon.component.css'],
  standalone: true,
  imports: [MatIcon, NgClass],
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
