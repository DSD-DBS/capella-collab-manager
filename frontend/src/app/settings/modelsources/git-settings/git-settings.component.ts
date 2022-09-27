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
  GitSettings,
  GitSettingsService,
} from 'src/app/services/settings/git-settings.service';
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
      this.urlValidator.bind(this),
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
    this.gitSettingsService.gitSettings.subscribe((gitSettings) => {
      this.cmpGitSettings = gitSettings;
    });

    this.gitSettingsService.loadGitSettings();
  }

  createGitSettings(): void {
    if (this.form.valid) {
      this.gitSettingsService
        .createGitSettings(
          (this.form.get('name') as FormControl).value,
          (this.form.get('url') as FormControl).value,
          (this.form.get('type') as FormControl).value
        )
        .subscribe(this.form.reset);
    }
  }

  deleteGitSettings(id: number): void {
    const toDeleteGitSetting: GitSettings = this.cmpGitSettings.find(
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

    if (this.cmpGitSettings === undefined) {
      return null;
    }

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
