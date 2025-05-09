/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  inject,
  input,
  output,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatRippleModule } from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TagHelperService } from 'src/app/helpers/tag/tag.service';

@Component({
  selector: 'app-tag',
  imports: [
    MatChipsModule,
    MatIconModule,
    MatTooltipModule,
    NgClass,
    MatButtonModule,
    MatRippleModule,
  ],
  templateUrl: './tag.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TagComponent {
  tagHelperService = inject(TagHelperService);

  hexBgColor = input<string>('#FFFFFF');
  name = input.required<string>();
  description = input<string | null>(null);
  textIcon = input<string | null>(null);
  actionIcon = input<string | null>(null);

  actionClick = output();
}
