/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { UntilDestroy } from '@ngneat/until-destroy';
import { absoluteUrlValidator } from 'src/app/helpers/validators/url-validator';
import { DeleteGitSettingsDialogComponent } from 'src/app/settings/modelsources/git-settings/delete-git-settings-dialog/delete-git-settings-dialog.component';
import {
  BasicGitInstance,
  GitInstance,
  GitInstancesService,
} from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

@UntilDestroy()
@Component({
  selector: 'app-git-settings',
  templateUrl: './git-settings.component.html',
  styleUrls: ['./git-settings.component.css'],
})
export class GitSettingsComponent implements OnInit {
  constructor(
    public dialog: MatDialog,
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>,
    public gitInstancesService: GitInstancesService,
  ) {}

  gitInstancesForm = new FormGroup({
    type: new FormControl('', Validators.required),
    name: new FormControl('', {
      validators: Validators.required,
      asyncValidators: this.gitInstancesService.asyncNameValidator(),
    }),
    url: new FormControl('', [Validators.required, absoluteUrlValidator()]),
    apiURL: new FormControl('', absoluteUrlValidator()),
  });

  ngOnInit(): void {
    this.gitInstancesService.loadGitInstances();
  }

  createGitInstance(): void {
    if (this.gitInstancesForm.valid) {
      let url = this.gitInstancesForm.value.url!;
      if (url.endsWith('/')) {
        url = url.slice(0, -1);
      }

      this.gitInstancesService
        .createGitInstance(this.gitInstancesForm.value as BasicGitInstance)
        .subscribe(() => this.gitInstancesForm.reset());
    }
  }

  deleteGitInstance(instance: GitInstance): void {
    const dialogRef = this.dialog.open(DeleteGitSettingsDialogComponent, {
      data: instance,
    });

    dialogRef.afterClosed().subscribe((response) => {
      if (response) {
        this.gitInstancesService.deleteGitInstance(instance.id).subscribe();
      }
    });
  }
}
