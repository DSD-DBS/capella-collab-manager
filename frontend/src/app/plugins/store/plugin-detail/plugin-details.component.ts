/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, take } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { EditPluginComponent } from 'src/app/plugins/store/edit-plugin/edit-plugin.component';
import { Plugin, PluginStoreService } from '../service/plugin-store.service';

@UntilDestroy()
@Component({
  selector: 'app-plugin-details',
  templateUrl: '../edit-plugin/edit-plugin.component.html',
  styleUrls: ['../edit-plugin/edit-plugin.component.css'],
})
export class PluginDetailsComponent extends EditPluginComponent {
  pluginDeletionPossible = true;
  plugin?: Plugin = undefined;

  constructor(
    pluginStoreService: PluginStoreService,
    router: Router,
    private toastService: ToastService,
    private dialog: MatDialog,
  ) {
    super(pluginStoreService, router);
  }

  ngOnInit(): void {
    this.pluginStoreService.plugin
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((plugin) => {
        this.plugin = plugin;
        this.editPluginForm.patchValue(plugin);
      });
    super.ngOnInit();
  }

  onSubmit() {
    if (this.editPluginForm.valid) {
      this.pluginStoreService
        .updatePlugin(this.plugin!.id, this.editPluginForm.value as Plugin)
        .subscribe(() => {
          this.toastService.showSuccess(
            'Plugin updated successfully',
            `The plugin '${this.plugin?.content?.metadata?.id}' was updated successfully.`,
          );
        });
    }
  }

  deletePlugin() {
    this.pluginStoreService.plugin
      .pipe(filter(Boolean), take(1))
      .subscribe((plugin) => {
        const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
          data: {
            title: 'Remove plugin',
            text: 'Do you really want to delete the plugin? All related pipelines in projects will be removed.',
            requiredInput: plugin?.content?.metadata?.id,
          },
        });
        dialogRef.afterClosed().subscribe((selection: boolean) => {
          if (!selection) return;
          this.pluginStoreService.deletePlugin(plugin.id).subscribe(() => {
            this.router.navigate(['/plugins']);
            this.pluginStoreService.fetchPluginsFromStore();
            this.toastService.showSuccess(
              'Plugin deleted successfully',
              `The plugin ${plugin.content?.metadata?.id} was deleted successfully.`,
            );
          });
        });
      });
  }
}
