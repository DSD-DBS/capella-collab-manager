/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import {
  BaseT4CInstance,
  NewT4CInstance,
  T4CInstance,
  T4CInstanceService,
} from '../../../../services/settings/t4c-model.service';
import {
  BehaviorSubject,
  filter,
  map,
  switchMap,
  tap,
  combineLatest,
} from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ToolService, Version } from 'src/app/services/tools/tool2.service';

@Component({
  selector: 'app-edit-t4c-instance',
  templateUrl: './edit-t4c-instance.component.html',
  styleUrls: ['./edit-t4c-instance.component.css'],
})
export class EditT4CInstanceComponent implements OnInit {
  editing: boolean = false;

  existing: boolean = false;

  _instance = new BehaviorSubject<T4CInstance | undefined>(undefined);
  get instance() {
    return this._instance.value;
  }

  _capella_versions = new BehaviorSubject<Version[]>([]);
  get capella_versions() {
    return this._capella_versions.value;
  }

  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    version_id: new FormControl(-1, Validators.required),
    license: new FormControl('', Validators.required),
    host: new FormControl('', Validators.required),
    port: new FormControl(null as number | null, [
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
    username: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required),
  });

  constructor(
    private navBarService: NavBarService,
    private t4cInstanceService: T4CInstanceService,
    private route: ActivatedRoute,
    private router: Router,
    private toastService: ToastService,
    private toolService: ToolService
  ) {
    this.navBarService.title = 'Settings / Modelsources / T4C';

    // This has to happen in the constructor because of NG0100
    // https://angular.io/errors/NG0100
    this.route.params
      .pipe(
        map((params) => params.instance),
        filter((instance) => instance === undefined)
      )
      .subscribe({
        next: () =>
          (this.navBarService.title = 'Settings / Modelsources / T4C / Create'),
      });
  }

  ngOnInit(): void {
    this.route.params
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
      .get_versions()
      .pipe(
        filter(Boolean),
        map((versions) =>
          versions.filter((version: Version) => version.tool_id === 1)
        )
      )
      .subscribe(this._capella_versions);

    combineLatest([
      this._instance.pipe(
        filter(Boolean),
        tap((instance) => {
          this.navBarService.title = `Settings / Modelsources / T4C / ${instance.name}`;
        })
      ),
      this._capella_versions,
    ]).subscribe((instance: [T4CInstance, Version[]]) => {
      this.form.patchValue(instance[0]);
    });

    this.toolService.get_versions().subscribe(this.toolService._versions);
  }

  enableEditing(): void {
    this.editing = true;
    this.form.enable();
    this.form.controls.name.disable();
    this.form.controls.version_id.disable();
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
          this.router.navigate(['..'], { relativeTo: this.route });
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
}
