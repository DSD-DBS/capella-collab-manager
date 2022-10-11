/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
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
  public instances: GitSettings[];
  gitSettingsForm = new FormGroup({
    type: new FormControl('', Validators.required),
    name: new FormControl('', Validators.required),
    url: new FormControl('', Validators.required),
  });

  constructor(
    private navbarService: NavBarService,
    private gitSettingsService: GitSettingsService,
    public dialog: MatDialog,
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>
  ) {
    this.navbarService.title = 'Settings / Modelsources / Git';
    this.instances = [];
  }

  ngOnInit(): void {
    this.gitSettingsService.listGitSettings().subscribe((res) => {
      res.forEach((instance) => {
        this.instances.push(instance);
      });
    });
  }

  createGitSettings(): void {
    if (this.gitSettingsForm.valid) {
      this.gitSettingsService
        .createGitSettings(
          (this.gitSettingsForm.get('name') as FormControl).value,
          (this.gitSettingsForm.get('url') as FormControl).value,
          (this.gitSettingsForm.get('type') as FormControl).value
        )
        .subscribe((res) => {
          this.gitSettingsForm.reset();
          this.instances.push(res);
        });
    }
  }

  deleteGitSettings(id: number): void {
    const index: number = this.instances.findIndex((obj) => obj.id == id);
    this.dialog
      .open(DeleteGitSettingsDialogComponent, {
        data: this.instances[index],
      })
      .afterClosed()
      .subscribe((response) => {
        if (response) {
          this.gitSettingsService.deleteGitSettings(id).subscribe((_) => {
            this.instances.splice(index, 1);
          });
        }
      });
  }
}
