/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import {
  GitSetting,
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
    this.gitSettingsSubscription = this.gitSettingsService.gitSetting.subscribe(
      {
        next: (gitSetting: GitSetting) => {
          this.gitSettingsForm.controls['type'].setValue(
            gitSetting.type as string
          );
          this.gitSettingsForm.controls['name'].setValue(gitSetting.name);
          this.gitSettingsForm.controls['url'].setValue(gitSetting.url);
          this.breadcrumbsService.updatePlaceholder({ gitSetting });
        },
      }
    );

    this.paramsSubscription = this.route.params.subscribe((params) => {
      this.id = params['id'];
      if (!!this.id) {
        this.gitSettingsService.loadGitSettingById(this.id);
      }
    });
  }

  ngOnDestroy(): void {
    this.gitSettingsSubscription?.unsubscribe();
    this.paramsSubscription?.unsubscribe();
    this.breadcrumbsService.updatePlaceholder({ gitSetting: undefined });
  }

  editGitSettings() {
    this.gitSettingsService
      .editGitSettings(
        this.id,
        (this.gitSettingsForm.get('name') as FormControl).value,
        (this.gitSettingsForm.get('url') as FormControl).value,
        (this.gitSettingsForm.get('type') as FormControl).value
      )
      .subscribe((_) => this.goBack());
  }

  goBack(): void {
    this.router.navigateByUrl('/settings/modelsources/git');
  }
}
