/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import {
  MatFormField,
  MatLabel,
  MatError,
  MatHint,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, map, take } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  CreateT4CInstance,
  PatchT4CInstance,
  Protocol,
  SettingsModelsourcesT4CInstancesService,
  ToolVersion,
} from 'src/app/openapi';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import { ToolWrapperService } from 'src/app/settings/core/tools-settings/tool.service';
import { T4CLicenseServerWrapperService } from '../../../../services/settings/t4c-license-server.service';
import { T4CInstanceSettingsComponent } from '../t4c-instance-settings/t4c-instance-settings.component';

@UntilDestroy()
@Component({
  selector: 'app-edit-t4c-instance',
  templateUrl: './edit-t4c-instance.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatError,
    MatSelect,
    MatOption,
    MatHint,
    MatButton,
    MatIcon,
    T4CInstanceSettingsComponent,
    AsyncPipe,
  ],
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
    name: new FormControl('', {
      validators: Validators.required,
      asyncValidators: this.t4cInstanceWrapperService.asyncNameValidator(),
    }),
    version_id: new FormControl(-1, [Validators.required, Validators.min(0)]),
    license_server_id: new FormControl(-1, [
      Validators.required,
      Validators.min(0),
    ]),
    protocol: new FormControl<Protocol>('ws', Validators.required),
    host: new FormControl('', Validators.required),
    port: new FormControl(2036, [Validators.required, ...this.portValidators]),
    cdo_port: new FormControl(12036, [
      Validators.required,
      ...this.portValidators,
    ]),
    http_port: new FormControl(8080, this.portValidators),
    rest_api: new FormControl('', [
      Validators.required,
      Validators.pattern(/^https?:\/\//),
    ]),
    username: new FormControl('', [Validators.required]),
    password: new FormControl('', [Validators.required]),
  });

  get protocols(): Protocol[] {
    return Object.values(Protocol);
  }

  constructor(
    public t4cInstanceWrapperService: T4CInstanceWrapperService,
    public t4cLicenseServerWrapperService: T4CLicenseServerWrapperService,
    private t4cInstanceService: SettingsModelsourcesT4CInstancesService,
    private route: ActivatedRoute,
    private router: Router,
    private toastService: ToastService,
    private toolService: ToolWrapperService,
    private breadcrumbsService: BreadcrumbsService,
    private dialog: MatDialog,
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
        this.t4cInstanceWrapperService.loadInstance(instanceId);
      });

    this.t4cInstanceWrapperService.t4cInstance$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((initialT4CInstance) => {
        const t4cInstance = {
          ...initialT4CInstance,
          password: '***********',
          version_id: initialT4CInstance.version.id,
          license_server_id: initialT4CInstance.license_server.id,
        };
        this.isArchived = t4cInstance.is_archived;
        this.form.patchValue(t4cInstance);
        this.form.controls.name.setAsyncValidators(
          this.t4cInstanceWrapperService.asyncNameValidator(t4cInstance),
        );
        this.breadcrumbsService.updatePlaceholder({ t4cInstance });
      });

    this.toolService
      .getVersionsForTool(1, false)
      .pipe(filter(Boolean))
      .subscribe((capellaVersions) => (this.capellaVersions = capellaVersions));
  }

  enableEditing(): void {
    this.editing = true;
    this.form.enable();
    this.form.controls.version_id.disable();

    this.form.controls.password.patchValue('');
    this.form.controls.password.removeValidators(Validators.required);
    this.form.controls.password.updateValueAndValidity();
  }

  cancelEditing(): void {
    this.editing = false;
    this.form.disable();

    if (this.instanceId) {
      this.t4cInstanceWrapperService.loadInstance(this.instanceId);
    }
  }

  create(): void {
    if (this.form.valid) {
      this.t4cInstanceWrapperService
        .createInstance(this.form.value as CreateT4CInstance)
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
      this.t4cInstanceWrapperService
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
      this.t4cInstanceWrapperService
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
    this.t4cInstanceWrapperService.resetT4CInstance();
    this.breadcrumbsService.updatePlaceholder({ t4cInstance: undefined });
  }

  deleteT4CRepository(): void {
    this.t4cInstanceWrapperService.t4cInstance$
      .pipe(take(1), untilDestroyed(this))
      .subscribe((instance) => {
        if (!instance) {
          return;
        }
        const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
          data: {
            title: 'Delete TeamForCapella Server Instance',
            text:
              `Do you really want to remove the integration of the TeamForCapella server '${instance?.name}'? ` +
              'This will remove all integrations of related repositories in projects. ' +
              'Repositories will no longer be injected into sessions and no session token will be issues for the repository anymore. ' +
              'The server itself will not be removed, only the link between the Capella Collaboration Manager and the TeamForCapella server.',
          },
        });

        dialogRef.afterClosed().subscribe((result: boolean) => {
          if (result) {
            this.t4cInstanceService.deleteT4cInstance(instance.id).subscribe({
              next: () => {
                this.toastService.showSuccess(
                  `TeamForCapella instance removed`,
                  `The TeamForCapella instance '${instance.name}' and all related repositories have been removed.`,
                );
                this.t4cInstanceWrapperService.loadInstances();
                this.router.navigateByUrl('/settings/modelsources/t4c');
              },
            });
          }
        });
      });
  }
}
