/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { UntilDestroy } from '@ngneat/until-destroy';
import { EditPluginComponent } from 'src/app/plugins/store/edit-plugin/edit-plugin.component';

@UntilDestroy()
@Component({
  selector: 'app-create-plugin',
  templateUrl: '../edit-plugin/edit-plugin.component.html',
  styleUrls: ['../edit-plugin/edit-plugin.component.css'],
})
export class CreatePluginComponent extends EditPluginComponent {
  editPluginForm = new FormGroup({
    remote: new FormControl('', Validators.required),
    username: new FormControl(''),
    password: new FormControl(''),
  });
}
