/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, Input } from '@angular/core';
import { MatTooltip } from '@angular/material/tooltip';
import { formatDistanceToNow, format } from 'date-fns';
import { DateArg } from 'date-fns/types';

@Component({
  selector: 'app-relative-time',
  standalone: true,
  imports: [MatTooltip],
  templateUrl: './relative-time.component.html',
})
export class RelativeTimeComponent {
  @Input() date?: DateArg<Date>;
  @Input() suffix = true;

  get relativeTime(): string {
    if (!this.date) return '';
    return formatDistanceToNow(this.date, { addSuffix: this.suffix });
  }

  get absoluteTime(): string {
    if (!this.date) return '';
    return format(this.date, 'PPpp');
  }
}