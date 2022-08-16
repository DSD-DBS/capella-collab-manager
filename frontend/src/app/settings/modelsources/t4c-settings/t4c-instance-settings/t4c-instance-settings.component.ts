// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit, ViewChild } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  FormGroupDirective,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import {
  T4CRepoService,
  T4CRepository,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { T4CSyncService } from 'src/app/services/t4c-sync/t4-csync.service';
import { ActivatedRoute } from '@angular/router';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import { T4CRepoDeletionDialogComponent } from './t4c-repo-deletion-dialog/t4c-repo-deletion-dialog.component';

@Component({
  selector: 'app-t4c-instance-settings',
  templateUrl: './t4c-instance-settings.component.html',
  styleUrls: ['./t4c-instance-settings.component.css'],
})
export class T4CInstanceSettingsComponent implements OnInit {
  constructor(
    private t4cSyncService: T4CSyncService,
    public t4cRepoService: T4CRepoService,
    private dialog: MatDialog,
    private route: ActivatedRoute,
    private navbarService: NavBarService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.instance_id = params['id'];
      this.navbarService.title =
        'Settings / Modelsources / T4C / Instances / ' + this.instance_id;
    });
  }

  @ViewChild('repositoryList') repositoryList: any;

  instance_id: number = -1;
  synchronizeButtonState = 'primary';

  synchronizeRepositories() {
    this.t4cSyncService.syncRepositories().subscribe(() => {
      this.synchronizeButtonState = 'success';
      setTimeout(() => {
        this.synchronizeButtonState = 'primary';
      }, 3000);
    });
  }

  createRepositoryForm = new FormGroup({
    name: new FormControl('', Validators.required),
  });

  projectNonexistenceValidator(): Validators {
    return (control: AbstractControl): ValidationErrors | null => {
      for (let repo of this.t4cRepoService.repositories) {
        if (repo.name == control.value) {
          return { projectExistsError: true };
        }
      }
      return null;
    };
  }

  refreshRepositories(): void {
    this.t4cRepoService.getT4CRepositories(this.instance_id).subscribe();
  }

  createRepository(formDirective: FormGroupDirective): void {
    if (this.createRepositoryForm.valid) {
      this.t4cRepoService
        .createT4CRepository(
          this.createRepositoryForm.value.name,
          this.instance_id
        )
        .subscribe(() => {
          this.refreshRepositories();
          formDirective.resetForm();
          this.createRepositoryForm.reset();
        });
    }
  }

  removeRepository(project: T4CRepository): void {
    const dialogRef = this.dialog.open(T4CRepoDeletionDialogComponent, {
      data: project,
    });

    dialogRef.afterClosed().subscribe((val) => {
      if (val) {
        this.refreshRepositories();
      }
    });
  }

  get selectedRepository(): T4CRepository {
    return this.repositoryList.selectedOptions.selected[0].value;
  }
}
