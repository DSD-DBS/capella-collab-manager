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
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import { absoluteUrlValidator } from 'src/app/helpers/validators/url-validator';
import { DeleteGitSettingsDialogComponent } from 'src/app/settings/modelsources/git-settings/delete-git-settings-dialog/delete-git-settings-dialog.component';
import {
  GitInstance,
  GitInstancesService,
  GitType,
} from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

@UntilDestroy()
@Component({
  selector: 'app-git-settings',
  templateUrl: './git-settings.component.html',
  styleUrls: ['./git-settings.component.css'],
})
export class GitSettingsComponent implements OnInit {
  public availableGitSettings: GitInstance[] = [];

  gitInstancesForm = new FormGroup({
    type: new FormControl('', Validators.required),
    name: new FormControl('', [Validators.required, this.nameValidator()]),
    url: new FormControl('', [Validators.required, absoluteUrlValidator()]),
    apiURL: new FormControl('', absoluteUrlValidator()),
  });

  constructor(
    private gitSettingsService: GitInstancesService,
    public dialog: MatDialog,
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>
  ) {}

  ngOnInit(): void {
    this.gitSettingsService.gitInstances
      .pipe(filter(Boolean), untilDestroyed(this))
      .subscribe((gitInstances) => {
        this.availableGitSettings = gitInstances;
      });

    this.gitSettingsService.loadGitInstances();
  }

  createGitSettings(): void {
    if (this.gitInstancesForm.valid) {
      let url = this.gitInstancesForm.value.url!;
      if (url.endsWith('/')) {
        url = url.slice(0, -1);
      }

      this.gitSettingsService
        .createGitInstance({
          name: this.gitInstancesForm.value.name!,
          url: url,
          apiURL: this.gitInstancesForm.value.apiURL!,
          type: this.gitInstancesForm.value.type as GitType,
        })
        .subscribe(() => this.gitInstancesForm.reset());
    }
  }

  deleteGitSettings(id: number): void {
    const toDeleteGitSetting: GitInstance = this.availableGitSettings.find(
      (gitSetting) => gitSetting.id == id
    )!;
    this.dialog
      .open(DeleteGitSettingsDialogComponent, {
        data: toDeleteGitSetting,
      })
      .afterClosed()
      .subscribe((response) => {
        if (response) {
          this.gitSettingsService.deleteGitInstance(id).subscribe();
        }
      });
  }

  nameValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const existingGitSetting = this.availableGitSettings.find(
        (gitSetting) => gitSetting.name == control.value
      );

      if (existingGitSetting) {
        return { uniqueName: { value: existingGitSetting.name } };
      }
      return null;
    };
  }
}
