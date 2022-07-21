// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import {
  GitSettings,
  GitSettingsService,
  GitType,
} from 'src/app/services/settings/git-settings.service';
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';

@Component({
  selector: 'app-git-settings',
  templateUrl: './git-settings.component.html',
  styleUrls: ['./git-settings.component.css'],
})
export class GitSettingsComponent implements OnInit {
  public instances: Array<GitSettings>;
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
          window.location.reload();
        });
    }
  }

  deleteGitSettings(id: number): void {
    this.gitSettingsService.deleteGitSettings(id).subscribe((_) => {
      delete this.instances[id];
    });
  }

  openDialog(id: number): void {
    const dialogRef = this.dialog.open(DialogDeleteGitSettings, {
      data: this.instances[id],
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.deleteGitSettings(id);
      }
    });
  }
}

@Component({
  selector: 'dialog-delete-git-settings',
  templateUrl: 'dialog-delete-git-settings.html',
})
export class DialogDeleteGitSettings {
  constructor(
    public dialogRef: MatDialogRef<DialogDeleteGitSettings>,
    @Inject(MAT_DIALOG_DATA) public data: GitSettings
  ) {}

  close(result: boolean): void {
    this.dialogRef.close(result);
  }
}
