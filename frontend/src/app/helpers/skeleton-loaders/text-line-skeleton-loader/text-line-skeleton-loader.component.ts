/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, Input } from '@angular/core';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

@Component({
  selector: 'app-text-line-skeleton-loader',
  templateUrl: './text-line-skeleton-loader.component.html',
  styleUrls: ['./text-line-skeleton-loader.component.css'],
  standalone: true,
  imports: [NgxSkeletonLoaderModule],
})
export class TextLineSkeletonLoaderComponent {
  @Input()
  width = '20%';
}
