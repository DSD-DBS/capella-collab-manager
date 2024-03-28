/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

@Component({
  selector: 'story-model-badge',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    NgxSkeletonLoaderModule,
    MatSlideToggleModule,
  ],
  templateUrl: './model-badge.component.html',
  styleUrls: ['./model-badge.component.css'],
})
export class ModelBadgeComponent {
  /**
   * The error message to display
   */
  @Input() errorMessage?: string;

  /**
   * The error code from the backend
   */
  @Input() errorCode?: string;

  /**
   * Whether the badge is currently loading
   */
  @Input() loading = false;

  /**
   * The content of the model complexity badge
   */
  @Input()
  complexityBadge?: string | ArrayBuffer | null;

  constructor() {}

  openModelComplexityBadgeDocs() {
    window.open('/docs/projects/models/complexity_badge/', '_blank');
  }
}
