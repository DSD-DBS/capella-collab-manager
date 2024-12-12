/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { KeyValuePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  input,
  output,
} from '@angular/core';
import { MatCheckboxModule } from '@angular/material/checkbox';

@Component({
  selector: 'app-token-permission-selection',
  imports: [MatCheckboxModule, KeyValuePipe],
  templateUrl: './token-permission-selection.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TokenPermissionSelectionComponent {
  tokenPermissions = input.required<TokenProperties>();
  scope = input.required<string>();

  selectionChange = output<TokenPermissionSelectionEvent>();

  userTokenVerbs: UserTokenVerb[] = ['GET', 'CREATE', 'UPDATE', 'DELETE'];
}

export type TokenProperties = Record<
  string,
  {
    title: string;
    description: string;
    items: {
      enum?: UserTokenVerb[];
      const?: UserTokenVerb;
    };
  }
>;

export type UserTokenVerb = 'GET' | 'CREATE' | 'UPDATE' | 'DELETE';

export interface TokenPermissionSelectionEvent {
  scope: string;
  permission: string;
  verb: UserTokenVerb;
  checked: boolean;
}
