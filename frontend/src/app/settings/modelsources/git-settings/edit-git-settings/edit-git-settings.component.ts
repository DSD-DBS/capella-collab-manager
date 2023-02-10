/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { filter, Subscription } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import {
  GitInstance,
  GitSettingsService,
} from 'src/app/services/settings/git-settings.service';

@Component({
  selector: 'app-edit-git-settings',
  templateUrl: './edit-git-settings.component.html',
  styleUrls: ['./edit-git-settings.component.css'],
})
export class EditGitSettingsComponent implements OnInit, OnDestroy {
  id: number = -1;

  gitSettingsForm = new FormGroup({
    type: new FormControl('', Validators.required),
    name: new FormControl('', Validators.required),
    url: new FormControl('', Validators.required),
    apiURL: new FormControl(''),
  });

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private gitSettingsService: GitSettingsService,
    private breadcrumbsService: BreadcrumbsService
  ) {}

  private gitSettingsSubscription?: Subscription;
  private paramsSubscription?: Subscription;

  ngOnInit(): void {
    this.gitSettingsSubscription = this.gitSettingsService.gitSetting
      .pipe(filter(Boolean))
      .subscribe((instance: GitInstance) => {
        this.gitSettingsForm.patchValue(instance);
        this.breadcrumbsService.updatePlaceholder({ gitInstance: instance });
      });

    this.paramsSubscription = this.route.params.subscribe((params) => {
      this.id = params['id'];
      if (!!this.id) {
        this.gitSettingsService.loadGitInstanceById(this.id);
      }
    });
  }

  ngOnDestroy(): void {
    this.gitSettingsSubscription?.unsubscribe();
    this.paramsSubscription?.unsubscribe();
    this.breadcrumbsService.updatePlaceholder({ gitInstance: undefined });
  }

  editGitSettings() {
    this.gitSettingsService
      .editGitInstance({
        ...this.gitSettingsForm.value,
        id: this.id,
      } as GitInstance)
      .subscribe((_) => this.goBack());
  }

  goBack(): void {
    this.router.navigateByUrl('/settings/modelsources/git');
  }
}
