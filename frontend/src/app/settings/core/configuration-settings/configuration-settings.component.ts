/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit, ViewChild } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { EditorComponent } from 'src/app/helpers/editor/editor.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ConfigurationService } from 'src/app/openapi';
import { EditorComponent as EditorComponent_1 } from '../../../helpers/editor/editor.component';
import { UnifiedConfigWrapperService } from '../../../services/unified-config-wrapper/unified-config-wrapper.service';

@Component({
  selector: 'app-configuration-settings',
  templateUrl: './configuration-settings.component.html',
  imports: [EditorComponent_1, MatButton, MatIcon],
})
export class ConfigurationSettingsComponent implements OnInit {
  @ViewChild(EditorComponent) editor: EditorComponent | undefined;

  constructor(
    private configurationSettingsService: ConfigurationService,
    private toastService: ToastService,
    private unifiedConfigService: UnifiedConfigWrapperService,
  ) {}

  ngOnInit(): void {
    this.fetchConfiguration();
  }

  fetchConfiguration() {
    this.configurationSettingsService.getConfiguration().subscribe((data) => {
      this.editor!.value = data;
    });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  submitValue(value: any) {
    this.configurationSettingsService.updateConfiguration(value).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Configuration successfully updated',
          'The global configuration has been successfully updated. The metadata will be reloaded.',
        );
        this.fetchConfiguration();
        this.unifiedConfigService.loadUnifiedConfig().subscribe();
      },
    });
  }
}
