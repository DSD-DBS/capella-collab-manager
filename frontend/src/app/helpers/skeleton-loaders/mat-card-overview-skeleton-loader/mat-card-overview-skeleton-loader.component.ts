/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, HostListener, Input, OnInit } from '@angular/core';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

@Component({
  selector: 'app-mat-card-overview-skeleton-loader',
  templateUrl: './mat-card-overview-skeleton-loader.component.html',
  standalone: true,
  imports: [NgxSkeletonLoaderModule],
})
export class MatCardOverviewSkeletonLoaderComponent implements OnInit {
  @Input() loading = true;
  @Input() reservedCards = 1;

  @Input() rows: number | undefined = undefined;

  _cardNumbersArray: number[] = [];
  set cardsNumber(value: number) {
    this._cardNumbersArray = [...Array(value).keys()];
  }

  ngOnInit(): void {
    this.resize(window.innerWidth, window.innerHeight);
  }

  @HostListener('window:resize', ['$event'])
  onresize(event: Event) {
    if (event.target) {
      const target = event.target as Window;
      this.resize(target.innerWidth, target.innerHeight);
    }
  }

  resize(width: number, height: number) {
    // Margin is 1vw (left + right) and 1vh (top + bottom)

    const cardsPerColumn = this.rows ? this.rows : (0.98 * height - 120) / 275;
    const cardsPerRow = (0.98 * width) / 425;

    this.cardsNumber =
      Math.trunc(cardsPerColumn) * Math.trunc(cardsPerRow) - this.reservedCards;
  }
}
