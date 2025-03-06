/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { KeyValuePipe } from '@angular/common';
import { Component, inject, input, output } from '@angular/core';
import { MatButton } from '@angular/material/button';
import {
  MatExpansionPanel,
  MatExpansionPanelHeader,
  MatExpansionPanelTitle,
} from '@angular/material/expansion';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { tap } from 'rxjs';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { RelativeTimeComponent } from '../../../general/relative-time/relative-time.component';
import { ToastService } from '../../../helpers/toast/toast.service';
import {
  AdminScopesOutput,
  FineGrainedResourceOutput,
  GlobalTokensService,
  ProjectUserScopesOutput,
  UserScopesOutput,
  UsersTokenService,
  UserToken,
} from '../../../openapi';
import { UserTokenVerb } from '../token-permission-selection/token-permission-selection.component';

@Component({
  selector: 'app-token-card',
  imports: [
    KeyValuePipe,
    MatButton,
    MatExpansionPanel,
    MatExpansionPanelHeader,
    MatExpansionPanelTitle,
    MatIcon,
    MatTooltip,
    RelativeTimeComponent,
  ],
  templateUrl: './token-card.component.html',
})
export class TokenCardComponent {
  public token = input.required<UserToken>();
  public global = input<boolean>(false);
  tokenDeleted = output<void>();
  private tokenService = inject(UsersTokenService);
  private globalTokenService = inject(GlobalTokensService);
  private toastService = inject(ToastService);
  public ownUserWrapperService = inject(OwnUserWrapperService);

  isTokenExpired(expirationDate: string): boolean {
    return new Date(expirationDate) < new Date();
  }

  flattenScope(scope: FineGrainedResourceOutput): FlattenedScopes {
    const flattenedScopes: FlattenedScopes = {};
    flattenedScopes.user = scope.user;
    flattenedScopes.admin = scope.admin;
    for (const project in scope.projects) {
      flattenedScopes[project] = scope.projects[project];
    }
    return flattenedScopes;
  }

  countScopes(scopes: FlattenedScopes) {
    let counter = 0;
    for (const scope in scopes) {
      Object.values(scopes[scope]).forEach((element) => {
        counter += element.length;
      });
    }
    return counter;
  }

  containsVerb(
    scopes: FlattenedScopes,
    scope: string,
    permission: string,
    verb: UserTokenVerb,
  ) {
    const resolvedScope = scopes[scope];
    const resolvedPermission = Object.entries(resolvedScope).find(
      (element) => element[0] === permission,
    );
    if (!resolvedPermission) {
      return false;
    }
    return !!resolvedPermission[1].find((element) => element === verb);
  }

  deleteToken(token: UserToken) {
    if (this.global()) {
      this.globalTokenService
        .deleteTokenGlobally(token.id)
        .pipe(tap(() => this.tokenDeleted.emit()))
        .subscribe(() => {
          this.toastService.showSuccess(
            'Token deleted',
            `The token ${token.description} was successfully deleted!`,
          );
        });
    } else {
      this.tokenService
        .deleteTokenForUser(token.id)
        .pipe(tap(() => this.tokenDeleted.emit()))
        .subscribe(() => {
          this.toastService.showSuccess(
            'Token deleted',
            `The token ${token.description} was successfully deleted!`,
          );
        });
    }
  }
}

type FlattenedScopes = Record<
  string,
  UserScopesOutput | AdminScopesOutput | ProjectUserScopesOutput
>;
