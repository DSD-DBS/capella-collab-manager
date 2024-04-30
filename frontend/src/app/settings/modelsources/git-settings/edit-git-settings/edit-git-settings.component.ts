/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import {
  FormBuilder,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import {
  GitInstance,
  GitInstancesService,
} from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

@UntilDestroy()
@Component({
  selector: 'app-edit-git-settings',
  templateUrl: './edit-git-settings.component.html',
  styleUrls: ['./edit-git-settings.component.css'],
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatSelect,
    MatOption,
    MatInput,
    NgIf,
    MatError,
    MatButton,
  ],
})
export class EditGitSettingsComponent implements OnInit, OnDestroy {
  id = -1;

  gitInstanceForm = this.fb.group({
    type: ['', Validators.required],
    name: ['', Validators.required],
    url: ['', Validators.required],
    apiURL: [''],
  });

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private gitInstancesService: GitInstancesService,
    private breadcrumbsService: BreadcrumbsService,
    private fb: FormBuilder,
  ) {}

  ngOnInit(): void {
    this.gitInstancesService.gitInstance$
      .pipe(filter(Boolean), untilDestroyed(this))
      .subscribe((instance: GitInstance & { api_url?: string }) => {
        if (instance.api_url) {
          instance.apiURL = instance.api_url;
        }

        this.gitInstanceForm.controls.name.addAsyncValidators(
          this.gitInstancesService.asyncNameValidator(instance),
        );

        this.gitInstanceForm.patchValue(instance);
        this.breadcrumbsService.updatePlaceholder({ gitInstance: instance });
      });

    this.route.params
      .pipe(
        untilDestroyed(this),
        map((params) => parseInt(params.id)),
      )
      .subscribe((instanceId) => {
        this.gitInstancesService.loadGitInstanceById(instanceId);
        this.id = instanceId;
      });

    this.gitInstancesService.loadGitInstances();
  }

  ngOnDestroy(): void {
    this.breadcrumbsService.updatePlaceholder({ gitInstance: undefined });
  }

  editGitInstance() {
    this.gitInstancesService
      .editGitInstance({
        ...this.gitInstanceForm.value,
        id: this.id,
      } as GitInstance)
      .subscribe(() =>
        this.router.navigate(['../..'], { relativeTo: this.route }),
      );
  }
}
