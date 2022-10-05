/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import {
  GitSetting,
  GitSettingsService,
  GitType,
} from 'src/app/services/settings/git-settings.service';
import { absoluteUrlSafetyValidator } from 'src/app/helpers/validators/url-validator';
import { DeleteGitSettingsDialogComponent } from 'src/app/settings/modelsources/git-settings/delete-git-settings-dialog/delete-git-settings-dialog.component';

@Component({
  selector: 'app-git-settings',
  templateUrl: './git-settings.component.html',
  styleUrls: ['./git-settings.component.css'],
})
export class GitSettingsComponent implements OnInit {
  public cmpGitSettings: GitSettings[];

  form = new FormGroup({
    type: new FormControl('', Validators.required),
    name: new FormControl('', [
      Validators.required,
      this.nameValidator.bind(this),
    ]),
    url: new FormControl('', [
      Validators.required,
      absoluteUrlSafetyValidator(),
    ]),
  });

  constructor(
    private navbarService: NavBarService,
    private gitSettingsService: GitSettingsService,
    public dialog: MatDialog,
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>
  ) {
    this.navbarService.title = 'Settings / Modelsources / Git';
    this.cmpGitSettings = [];
  }

  ngOnInit(): void {
    this.gitSettingsService.gitSettings.subscribe({
      next: (gitSettings) => {
        this.cmpGitSettings = gitSettings;
      },
    });

    this.gitSettingsService.loadGitSettings();
  }

  createGitSettings(): void {
    if (this.form.valid) {
      let url = this.form.value.url!;
      if (url.endsWith('/')) {
        url = url.slice(0, -1);
      }

      this.gitSettingsService
        .createGitSettings({
          name: this.form.value.name!,
          url: url,
          type: this.form.value.type as GitType,
        })
        .subscribe((_) => this.form.reset());
    }
  }

  deleteGitSettings(id: number): void {
    const toDeleteGitSetting: GitSetting = this.cmpGitSettings.find(
      (gitSetting) => gitSetting.id == id
    )!;
    this.dialog
      .open(DeleteGitSettingsDialogComponent, {
        data: toDeleteGitSetting,
      })
      .afterClosed()
      .subscribe((response) => {
        if (response) {
          this.gitSettingsService.deleteGitSettings(id).subscribe((_) => {});
        }
      });
  }

  nameValidator(control: AbstractControl): ValidationErrors | null {
    let newInstanceName = control.value;
    let gitSettingNames: string[] = this.cmpGitSettings?.map(
      (gitSetting) => gitSetting.name
    );
    gitSettingNames ??= [];

    for (let gitSettingName of gitSettingNames) {
      if (gitSettingName == newInstanceName) {
        return { uniqueName: { value: gitSettingName } };
      }
    }
    return null;
  }

  urlValidator(control: AbstractControl): ValidationErrors | null {
    return null;
  }
}
