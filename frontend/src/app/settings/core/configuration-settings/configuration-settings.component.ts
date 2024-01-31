/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit, ViewChild } from '@angular/core';

import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { EditorComponent } from 'src/app/helpers/editor/editor.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ConfigurationSettingsService } from 'src/app/settings/core/configuration-settings/configuration-settings.service';

@Component({
  selector: 'app-configuration-settings',
  templateUrl: './configuration-settings.component.html',
})
export class ConfigurationSettingsComponent implements OnInit {
  @ViewChild(EditorComponent) editor: EditorComponent | undefined;

  constructor(
    private configurationSettingsService: ConfigurationSettingsService,
    private toastService: ToastService,
    private metadataService: MetadataService,
  ) {}

  ngOnInit(): void {
    this.fetchConfiguration();
  }

  fetchConfiguration() {
    this.configurationSettingsService
      .getConfigurationSettings('global')
      .subscribe((data) => {
        this.editor!.value = data;
      });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  submitValue(value: any) {
    this.configurationSettingsService
      .putConfigurationSettings('global', value)
      .subscribe({
        next: () => {
          this.toastService.showSuccess(
            'Configuration successfully updated',
            'The global configuration has been successfully updated. The metadata will be reloaded.',
          );
          this.fetchConfiguration();
          this.metadataService.loadBackendMetadata().subscribe();
        },
      });
  }
}
