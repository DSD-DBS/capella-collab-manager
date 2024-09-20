/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit, ViewChild } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { NavBarService } from 'src/app/general/nav-bar/nav-bar.service';
import { EditorComponent } from 'src/app/helpers/editor/editor.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ConfigurationSettingsService } from 'src/app/settings/core/configuration-settings/configuration-settings.service';
import { EditorComponent as EditorComponent_1 } from '../../../helpers/editor/editor.component';
import { FeedbackWrapperService } from '../../../sessions/feedback/feedback.service';

@Component({
  selector: 'app-configuration-settings',
  templateUrl: './configuration-settings.component.html',
  standalone: true,
  imports: [EditorComponent_1, MatButton, MatIcon],
})
export class ConfigurationSettingsComponent implements OnInit {
  @ViewChild(EditorComponent) editor: EditorComponent | undefined;

  constructor(
    private configurationSettingsService: ConfigurationSettingsService,
    private toastService: ToastService,
    private metadataService: MetadataService,
    private navbarService: NavBarService,
    private feedbackService: FeedbackWrapperService,
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
          this.navbarService.loadNavbarConfig().subscribe();
          this.feedbackService.loadFeedbackConfig().subscribe();
        },
      });
  }
}
