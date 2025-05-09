/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { TagComponent } from 'src/app/helpers/tag/tag.component';
import { Tag } from 'src/app/openapi';

@Component({
  selector: 'app-tag-display',
  imports: [TagComponent],
  templateUrl: './tag-display.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TagDisplayComponent {
  tag = input.required<Tag>();
}
