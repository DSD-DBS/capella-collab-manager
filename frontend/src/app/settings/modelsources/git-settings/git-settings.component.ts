/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgFor, AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import {
  MatIconAnchor,
  MatIconButton,
  MatButton,
} from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { RouterLink } from '@angular/router';
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
  standalone: true,
  imports: [
    NgIf,
    NgFor,
    MatIconAnchor,
    RouterLink,
    MatIcon,
    MatIconButton,
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatSelect,
    MatOption,
    MatInput,
    MatError,
    MatButton,
    AsyncPipe,
  ],
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
