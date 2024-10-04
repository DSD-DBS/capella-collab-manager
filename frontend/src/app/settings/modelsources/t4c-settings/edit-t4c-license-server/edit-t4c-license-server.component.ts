/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, JsonPipe, NgIf } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatRipple } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatError, MatFormField, MatLabel } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatTooltip } from '@angular/material/tooltip';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { filter, map, take } from 'rxjs';
import { BreadcrumbsService } from '../../../../general/breadcrumbs/breadcrumbs.service';
import { ConfirmationDialogComponent } from '../../../../helpers/confirmation-dialog/confirmation-dialog.component';
import { MatIconComponent } from '../../../../helpers/mat-icon/mat-icon.component';
import { ToastService } from '../../../../helpers/toast/toast.service';
import { SettingsModelsourcesT4CLicenseServersService } from '../../../../openapi';
import { T4CLicenseServerWrapperService } from '../../../../services/settings/t4c-license-server.service';

@UntilDestroy()
@Component({
  selector: 'app-edit-t4c-license-server',
  templateUrl: './edit-t4c-license-server.component.html',
  standalone: true,
  imports: [
    MatFormField,
    MatLabel,
    FormsModule,
    ReactiveFormsModule,
    MatButton,
    MatInput,
    MatError,
    MatIcon,
    AsyncPipe,
    NgIf,
    JsonPipe,
    NgxSkeletonLoaderModule,
    MatIconComponent,
    MatRipple,
    RouterLink,
    MatTooltip,
  ],
})
export class EditT4cLicenseServerComponent implements OnInit, OnDestroy {
  form: FormGroup;
  existing = false;
  editing = false;
  licenseServerId: number | null = null;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    public t4cLicenseServerWrapperService: T4CLicenseServerWrapperService,
    private t4cLicenseServerService: SettingsModelsourcesT4CLicenseServersService,
    private toastService: ToastService,
    private breadcrumbsService: BreadcrumbsService,
    private dialog: MatDialog,
  ) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      usage_api: ['', [Validators.required, Validators.pattern('https?://.+')]],
      license_key: ['', Validators.required],
    });
  }

  ngOnInit(): void {
    this.route.params
      .pipe(
        map((params) => params.licenseServer),
        filter(Boolean),
      )
      .subscribe((licenseServerId) => {
        this.existing = true;
        this.form.disable();

        this.licenseServerId = licenseServerId;
        this.t4cLicenseServerWrapperService.loadLicenseServer(licenseServerId);
      });

    this.route.params.subscribe((params) => {
      if (params['id']) {
        this.licenseServerId = +params['id'];
        this.existing = true;
        this.loadLicenseServer(this.licenseServerId);
      }
    });

    this.t4cLicenseServerWrapperService.licenseServer$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((licenseServer) => {
        this.form.patchValue(licenseServer);
        this.form.controls.name.setAsyncValidators(
          this.t4cLicenseServerWrapperService.asyncNameValidator(licenseServer),
        );
        this.breadcrumbsService.updatePlaceholder({ licenseServer });
      });
  }

  loadLicenseServer(id: number): void {
    this.t4cLicenseServerWrapperService.loadLicenseServer(id);
    this.t4cLicenseServerWrapperService.licenseServer$.subscribe((server) => {
      if (server) {
        this.form.patchValue(server);
        this.form.disable();
      }
    });
  }

  enableEditing(): void {
    this.editing = true;
    this.form.enable();
  }

  cancelEditing(): void {
    this.editing = false;
    this.form.disable();
    if (this.licenseServerId) {
      this.loadLicenseServer(this.licenseServerId);
    }
  }

  submit(): void {
    if (this.form.valid) {
      if (this.existing) {
        this.update();
      } else {
        this.create();
      }
    }
  }

  create(): void {
    this.t4cLicenseServerWrapperService
      .createLicenseServer(this.form.value)
      .subscribe((server) => {
        this.toastService.showSuccess(
          'License Server created',
          `The license server “${server.name}” was created.`,
        );
        this.router.navigate(['..', 'license-server', server.id], {
          relativeTo: this.route,
        });
      });
  }

  update(): void {
    if (this.licenseServerId) {
      this.t4cLicenseServerWrapperService
        .updateLicenseServer(this.licenseServerId, this.form.value)
        .subscribe((server) => {
          this.editing = false;
          this.form.disable();
          this.toastService.showSuccess(
            'License Server updated',
            `The license server “${server.name}” was updated.`,
          );
        });
    }
  }

  deleteLicenseServer(): void {
    this.t4cLicenseServerWrapperService.licenseServer$
      .pipe(take(1), untilDestroyed(this))
      .subscribe((licenseServer) => {
        if (!licenseServer) {
          return;
        }
        const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
          data: {
            title: 'Disconnect TeamForCapella License Server',
            text:
              'Do you want to disconnect the TeamForCapella license server? ' +
              'This will not delete the license server itself.',
          },
        });

        dialogRef.afterClosed().subscribe((result: boolean) => {
          if (result) {
            this.t4cLicenseServerService
              .deleteT4cLicenseServer(licenseServer.id)
              .subscribe({
                next: () => {
                  this.toastService.showSuccess(
                    `TeamForCapella License Server removed`,
                    `The TeamForCapella license server '${licenseServer.name}' has been removed.`,
                  );
                  this.t4cLicenseServerWrapperService.loadLicenseServers();
                  this.router.navigateByUrl('/settings/modelsources/t4c');
                },
              });
          }
        });
      });
  }

  ngOnDestroy() {
    this.t4cLicenseServerWrapperService.resetLicenseServer();
  }
}
