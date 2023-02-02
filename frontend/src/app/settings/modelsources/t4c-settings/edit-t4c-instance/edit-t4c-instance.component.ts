/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import {
  BehaviorSubject,
  filter,
  map,
  Subscription,
  switchMap,
  tap,
} from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  BaseT4CInstance,
  NewT4CInstance,
  Protocol,
  T4CInstance,
  T4CInstanceService,
} from 'src/app/services/settings/t4c-instance.service';
import {
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';

@Component({
  selector: 'app-edit-t4c-instance',
  templateUrl: './edit-t4c-instance.component.html',
  styleUrls: ['./edit-t4c-instance.component.css'],
})
export class EditT4CInstanceComponent implements OnInit, OnDestroy {
  editing: boolean = false;
  paramsSubscription?: Subscription;

  existing: boolean = false;

  _instance = new BehaviorSubject<T4CInstance | undefined>(undefined);
  get instance() {
    return this._instance.value;
  }

  _capella_versions = new BehaviorSubject<ToolVersion[]>([]);
  get capella_versions() {
    return this._capella_versions.value;
  }

  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    version_id: new FormControl(-1, Validators.required),
    license: new FormControl('', Validators.required),
    protocol: new FormControl<Protocol>('tcp', Validators.required),
    host: new FormControl('', Validators.required),
    port: new FormControl(2036, [
      Validators.required,
      Validators.pattern(/^\d*$/),
      Validators.min(0),
      Validators.max(65535),
    ]),
    cdo_port: new FormControl(12036, [
      Validators.required,
      Validators.pattern(/^\d*$/),
      Validators.min(0),
      Validators.max(65535),
    ]),
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
    private t4cInstanceService: T4CInstanceService,
    private route: ActivatedRoute,
    private router: Router,
    private toastService: ToastService,
    private toolService: ToolService,
    private breadcrumbsService: BreadcrumbsService
  ) {}

  ngOnInit(): void {
    this.paramsSubscription = this.route.params
      .pipe(
        map((params) => params.instance),
        filter(Boolean),
        tap(() => {
          this.existing = true;
          this.form.disable();
        }),
        switchMap((instance) => this.t4cInstanceService.getInstance(instance))
      )
      .subscribe(this._instance);

    this.toolService
      .getVersionsForTool(1)
      .pipe(filter(Boolean))
      .subscribe(this._capella_versions);

    this._instance
      .pipe(filter(Boolean))
      .subscribe((t4cInstance: T4CInstance) => {
        t4cInstance.password = '***********';
        this.form.patchValue(t4cInstance);
        this.breadcrumbsService.updatePlaceholder({ t4cInstance });
      });
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
    this.form.patchValue(this.instance as NewT4CInstance);
  }

  create(): void {
    if (this.form.valid) {
      this.t4cInstanceService
        .createInstance(this.form.value as NewT4CInstance)
        .subscribe((instance) => {
          this.toastService.showSuccess(
            'Instance created',
            `The instance “${instance.name}” was created.`
          );
          this._instance.next(instance);
          this.router.navigate(['..', 'instance', instance.id], {
            relativeTo: this.route,
          });
        });
    }
  }

  update(): void {
    if (this.form.valid) {
      this.t4cInstanceService
        .updateInstance(this.instance!.id, this.form.value as BaseT4CInstance)
        .subscribe((instance) => {
          this.editing = false;
          this.form.disable();
          this.toastService.showSuccess(
            'Instance updated',
            `The instance “${instance.name}” was updated.`
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
    this.paramsSubscription?.unsubscribe();
    this._instance.next(undefined);
    this.breadcrumbsService.updatePlaceholder({ t4cInstance: undefined });
  }
}
