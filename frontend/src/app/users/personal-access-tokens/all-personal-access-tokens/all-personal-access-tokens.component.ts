/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject, OnInit, model } from '@angular/core';
import { NgxSkeletonLoaderComponent } from 'ngx-skeleton-loader';
import { AllTokensService, UserToken } from '../../../openapi';
import { TokenCardComponent } from '../token-card/token-card.component';

@Component({
  selector: 'app-all-personal-access-tokens',
  imports: [TokenCardComponent, NgxSkeletonLoaderComponent],
  templateUrl: './all-personal-access-tokens.component.html',
})
export class AllPersonalAccessTokensComponent implements OnInit {
  tokens = model<UserToken[] | undefined>(undefined);
  public allTokensService = inject(AllTokensService);

  ngOnInit() {
    this.loadTokens();
  }

  loadTokens(): void {
    this.allTokensService.getAllTokens().subscribe({
      next: (token) => this.tokens.set(token),
      error: () => this.tokens.set(undefined),
    });
  }

  protected readonly Array = Array;
}
