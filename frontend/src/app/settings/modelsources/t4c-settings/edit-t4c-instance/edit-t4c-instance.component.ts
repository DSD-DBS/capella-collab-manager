/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  NewT4CInstance,
  PatchT4CInstance,
  Protocol,
  T4CInstanceService,
} from 'src/app/services/settings/t4c-instance.service';
import {
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';

@UntilDestroy()
@Component({
  selector: 'app-edit-t4c-instance',
  templateUrl: './edit-t4c-instance.component.html',
  styleUrls: ['./edit-t4c-instance.component.css'],
})
export class EditT4CInstanceComponent implements OnInit, OnDestroy {
  editing = false;
  existing = false;

  instanceId?: number;
  capellaVersions?: ToolVersion[];

  isArchived?: boolean;

  portValidators = [
    Validators.pattern(/^\d*$/),
    Validators.min(0),
    Validators.max(65535),
  ];

  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    version_id: new FormControl(-1, Validators.required),
    license: new FormControl('', Validators.required),
    protocol: new FormControl<Protocol>('tcp', Validators.required),
    host: new FormControl('', Validators.required),
    port: new FormControl(2036, [Validators.required, ...this.portValidators]),
    cdo_port: new FormControl(12036, [
      Validators.required,
      ...this.portValidators,
    ]),
    http_port: new FormControl<number | null>(null, this.portValidators),
    usage_api: new FormControl('', [
      Validators.required,
      Validators.pattern(/^https?:\/\//),
    ]),
    rest_api: new FormControl('', [
      Validators.required,
      Validators.pattern(/^https?:\/\//),
    ]),
    username: new FormControl('', [Validators.required]),
    password: new FormControl('', [Validators.required]),
  });

  constructor(
    public t4cInstanceService: T4CInstanceService,
    private route: ActivatedRoute,
    private router: Router,
    private toastService: ToastService,
    private toolService: ToolService,
    private breadcrumbsService: BreadcrumbsService,
  ) {}

  ngOnInit(): void {
    this.route.params
      .pipe(
        map((params) => params.instance),
        filter(Boolean),
      )
      .subscribe((instanceId) => {
        this.existing = true;
        this.form.disable();

        this.instanceId = instanceId;
        this.t4cInstanceService.loadInstance(instanceId);
      });

    this.t4cInstanceService.t4cInstance$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((t4cInstance) => {
        t4cInstance.password = '***********';
        this.isArchived = t4cInstance.is_archived;
        this.form.patchValue(t4cInstance);
        this.breadcrumbsService.updatePlaceholder({ t4cInstance });
      });

    this.toolService
      .getVersionsForTool(1)
      .pipe(filter(Boolean))
      .subscribe((capellaVersions) => (this.capellaVersions = capellaVersions));
  }

  enableEditing(): void {
    this.editing = true;
    this.form.enable();
    this.form.controls.name.disable();

    this.form.controls.password.patchValue('');
    this.form.controls.password.removeValidators(Validators.required);
    this.form.controls.password.updateValueAndValidity();
  }

  cancelEditing(): void {
    this.editing = false;
    this.form.disable();

    if (this.instanceId) {
      this.t4cInstanceService.loadInstance(this.instanceId);
    }
  }

  create(): void {
    if (this.form.valid) {
      this.t4cInstanceService
        .createInstance(this.form.value as NewT4CInstance)
        .subscribe((instance) => {
          this.toastService.showSuccess(
            'Instance created',
            `The instance “${instance.name}” was created.`,
          );
          this.router.navigate(['..', 'instance', instance.id], {
            relativeTo: this.route,
          });
        });
    }
  }

  update(): void {
    if (this.form.valid && this.instanceId) {
      this.t4cInstanceService
        .updateInstance(this.instanceId, this.form.value as PatchT4CInstance)
        .subscribe((instance) => {
          this.editing = false;
          this.form.disable();
          this.toastService.showSuccess(
            'Instance updated',
            `The instance “${instance.name}” was updated.`,
          );
        });
    }
  }

  toggleArchive(): void {
    if (this.instanceId) {
      this.t4cInstanceService
        .updateInstance(this.instanceId, {
          is_archived: !this.isArchived,
        })
        .subscribe((instance) => {
          this.isArchived = instance.is_archived;
          this.toastService.showSuccess(
            'Instance updated',
            `The instance “${instance.name}” is now ${
              this.isArchived ? 'archived' : 'unarchived'
            }.`,
          );
        });
    }
  }

  submit(): void {
    if (this.existing) {
      this.update();
    } else {
      this.create();
    }
  }

  ngOnDestroy(): void {
    this.t4cInstanceService.reset();
    this.breadcrumbsService.updatePlaceholder({ t4cInstance: undefined });
  }
}
