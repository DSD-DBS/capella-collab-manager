/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { PluginStoreService } from '../service/plugin-store.service';

@UntilDestroy()
@Component({
  selector: 'app-plugin-wrapper',
  templateUrl: './plugin-wrapper.component.html',
  styleUrls: ['./plugin-wrapper.component.css'],
})
export class PluginWrapperComponent implements OnInit, OnDestroy {
  constructor(
    private route: ActivatedRoute,
    public pluginStoreService: PluginStoreService,
    private breadcrumbsService: BreadcrumbsService,
  ) {}

  ngOnInit(): void {
    this.route.params
      .pipe(
        map((params) => params.plugin),
        untilDestroyed(this),
      )
      .subscribe((pluginId: number) => {
        this.pluginStoreService.fetchPluginFromStoreById(pluginId);
      });

    this.pluginStoreService.plugin
      .pipe(untilDestroyed(this))
      .subscribe((plugin) =>
        this.breadcrumbsService.updatePlaceholder({ plugin }),
      );
  }

  ngOnDestroy(): void {
    this.pluginStoreService.clearPlugin();
    this.breadcrumbsService.updatePlaceholder({
      plugin: undefined,
    });
  }
}
