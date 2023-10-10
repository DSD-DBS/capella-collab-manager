/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import {
  Tool,
  ToolIntegrations,
  ToolService,
} from 'src/app/settings/core/tools-settings/tool.service';

@Component({
  selector: 'app-tool-integrations',
  templateUrl: './tool-integrations.component.html',
  styleUrls: ['./tool-integrations.component.css'],
})
export class ToolIntegrationsComponent implements OnInit {
  constructor(private toolService: ToolService) {}

  _tool?: Tool = undefined;

  @Input()
  set tool(value: Tool | undefined) {
    if (this._tool && this._tool.id === value?.id) return;

    if (value) {
      this.loading = false;
      this.patchIntegrationsFormValues(value.integrations);
    }
    this._tool = value;
  }

  loading = true;

  public integrationsForm = new FormGroup({
    t4c: new FormControl(false),
    pv: new FormControl(false),
    pynb: new FormControl(false),
  });

  ngOnInit() {
    this.integrationsForm.valueChanges.subscribe(() => {
      this.patchToolIntegration();
    });
  }

  private patchIntegrationsFormValues(integrations: ToolIntegrations) {
    this.integrationsForm.patchValue({
      t4c: integrations.t4c,
      pv: integrations.pure_variants,
      pynb: integrations.jupyter,
    });
  }

  private mapIntegrationFormToPatchToolIntegrationObject() {
    return {
      t4c: this.integrationsForm.controls.t4c.value,
      pure_variants: this.integrationsForm.controls.pv.value,
      jupyter: this.integrationsForm.controls.pynb.value,
    };
  }

  public patchToolIntegration() {
    if (!this._tool) {
      return;
    }

    if (
      JSON.stringify(this._tool!.integrations) ===
      JSON.stringify(this.mapIntegrationFormToPatchToolIntegrationObject())
    ) {
      return;
    }

    this.loading = true;
    this.toolService
      .patchToolIntegrations(
        this._tool!.id,
        this.mapIntegrationFormToPatchToolIntegrationObject(),
      )
      .subscribe((integrations: ToolIntegrations) => {
        this._tool!.integrations = integrations;
        this.patchIntegrationsFormValues(integrations);

        this.loading = false;
      });
  }
}
