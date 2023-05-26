/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { debounceTime } from 'rxjs';
import {
  PluginStoreService,
  Plugin,
  PluginTemplateContent,
} from 'src/app/plugins/store/service/plugin-store.service';
import { stringify } from 'yaml';

@UntilDestroy()
@Component({
  selector: 'app-edit-plugin',
  templateUrl: './edit-plugin.component.html',
  styleUrls: ['./edit-plugin.component.css'],
})
export class EditPluginComponent {
  peekContent = '';
  loadingPeekContent = true;

  pluginDeletionPossible = false;

  constructor(
    public pluginStoreService: PluginStoreService,
    public router: Router,
  ) {}

  editPluginForm = new FormGroup({
    remote: new FormControl('', Validators.required),
    username: new FormControl(''),
    password: new FormControl(''),
  });

  ngOnInit(): void {
    this.editPluginForm.controls['remote'].valueChanges
      .pipe(debounceTime(500), untilDestroyed(this))
      .subscribe(() => {
        this.refreshPluginContent();
      });
  }

  onSubmit() {
    if (this.editPluginForm.valid) {
      this.pluginStoreService
        .registerPluginInStore(this.editPluginForm.value as Plugin)
        .subscribe(() => {
          this.pluginStoreService.fetchPluginsFromStore();
          this.router.navigate(['/plugins']);
        });
    }
  }

  refreshPluginContent() {
    this.loadingPeekContent = true;
    this.pluginStoreService
      .fetchPluginContentFromRemote(this.editPluginForm.value as Plugin)
      .pipe(untilDestroyed(this))
      .subscribe({
        next: (plugin) => {
          this.peekContent = this.prettifyYAML(plugin.content);
        },
        complete: () => {
          this.loadingPeekContent = false;
        },
      });
  }

  prettifyYAML(content: PluginTemplateContent | undefined): string {
    if (content === undefined) return '';
    return stringify(content);
  }

  deletePlugin() {
    console.error('Not implemented, only available in PlugingDetailsComponent');
  }
}
