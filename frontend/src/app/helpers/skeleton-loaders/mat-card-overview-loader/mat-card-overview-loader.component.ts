/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, HostListener, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-mat-card-overview-loader',
  templateUrl: './mat-card-overview-loader.component.html',
  styleUrls: ['./mat-card-overview-loader.component.css'],
})
export class MatCardOverviewLoaderComponent implements OnInit {
  @Input() loading = true;
  @Input() reservedCards = 1;

  @Input() rows: number | undefined = undefined;

  _cardNumbersArray: number[] = [];
  set cardsNumber(value: number) {
    this._cardNumbersArray = [...Array(value).keys()];
  }

  constructor() {}

  ngOnInit(): void {
    this.resize(window.innerWidth, window.innerHeight);
  }

  @HostListener('window:resize', ['$event'])
  onresize(event: any) {
    this.resize(event.target.innerWidth, event.target.innerHeight);
  }

  resize(width: number, height: number) {
    // Margin is 1vw (left + right) and 1vh (top + bottom)

    let cardsPerColumn = 0;
    if (this.rows) {
      cardsPerColumn = this.rows;
    } else {
      cardsPerColumn = (0.98 * height - 120) / 275;
    }

    const cardsPerRow = (0.98 * width) / 425;

    this.cardsNumber =
      Math.trunc(cardsPerColumn) * Math.trunc(cardsPerRow) - this.reservedCards;
  }
}
