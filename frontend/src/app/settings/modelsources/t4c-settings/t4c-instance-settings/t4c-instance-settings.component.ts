/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  OnInit,
  OnDestroy,
  ViewChild,
  Input,
  OnChanges,
  SimpleChanges,
} from '@angular/core';
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
  CreateT4CRepository,
  T4CRepoService,
  T4CRepository,
  T4CServerRepository,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { T4CSyncService } from 'src/app/services/t4c-sync/t4-csync.service';
import { T4CRepoDeletionDialogComponent } from './t4c-repo-deletion-dialog/t4c-repo-deletion-dialog.component';
import { T4CInstance } from 'src/app/services/settings/t4c-model.service';
import { tap, switchMap, BehaviorSubject } from 'rxjs';
import { MatSelectionList } from '@angular/material/list';

@Component({
  selector: 'app-t4c-instance-settings',
  templateUrl: './t4c-instance-settings.component.html',
  styleUrls: ['./t4c-instance-settings.component.css'],
})
export class T4CInstanceSettingsComponent implements OnChanges, OnDestroy {
  @Input() instance?: T4CInstance;

  constructor(
    private t4cSyncService: T4CSyncService,
    public t4cRepoService: T4CRepoService,
    private dialog: MatDialog
  ) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (this.instance) {
      this.t4cRepoService
        .getT4CRepositories(this.instance.id)
        .subscribe((repositories) => {
          this.t4cRepoService._repositories.next(repositories);
        });
    }
  }

  @ViewChild('repositoryList') repositoryList!: MatSelectionList;

  form = new FormGroup({
    name: new FormControl('', [
      Validators.required,
      this.uniqueNameValidator.bind(this),
      Validators.pattern(/^[-a-zA-Z0-9_]+$/),
    ]),
  });

  uniqueNameValidator(control: AbstractControl): ValidationErrors | null {
    return this.t4cRepoService.repositories
      .map((repo) => repo.name)
      .indexOf(control.value) >= 0
      ? { projectExistsError: true }
      : null;
  }

  refreshRepositories(): void {
    this.t4cRepoService._repositories.next(
      this.t4cRepoService.repositories.map((repo) => ({
        ...repo,
        status: undefined,
      }))
    );
    this.t4cRepoService
      .getT4CRepositories(this.instance!.id)
      .subscribe((repositories) => {
        this.t4cRepoService._repositories.next(repositories);
      });
  }

  createRepository(formDirective: FormGroupDirective): void {
    if (this.form.valid) {
      this.form.disable();

      this.t4cRepoService
        .createT4CRepository(
          this.instance!.id,
          this.form.value as CreateT4CRepository
        )
        .pipe(
          tap((repository) => {
            this.form.reset();
            this.form.enable();
            this.t4cRepoService._repositories.next([
              ...this.t4cRepoService.repositories,
              repository,
            ]);
          }),
          switchMap(() =>
            this.t4cRepoService.getT4CRepositories(this.instance!.id)
          )
        )
        .subscribe((repositories) => {
          this.t4cRepoService._repositories.next(repositories);
        });
    }
  }

  removeRepository(project: T4CRepository): void {
    const dialogRef = this.dialog.open(T4CRepoDeletionDialogComponent, {
      data: project,
    });

    dialogRef.afterClosed().subscribe((val) => {
      if (val) {
        this.t4cRepoService
          .getT4CRepositories(this.instance!.id)
          .subscribe((repositories) => {
            this.t4cRepoService._repositories.next(repositories);
          });
      }
    });
  }

  startRepository(repository: T4CServerRepository): void {
    this.repositoryList.selectedOptions.clear();
    delete repository.status;
    this.t4cRepoService
      .startRepository(repository.instance_id, repository.id)
      .pipe(
        tap(() => (repository.status = 'ONLINE')),
        switchMap(() =>
          this.t4cRepoService.getT4CRepositories(this.instance!.id)
        )
      )
      .subscribe((repositories) => {
        this.t4cRepoService._repositories.next(repositories);
      });
  }

  stopRepository(repository: T4CServerRepository): void {
    this.repositoryList.selectedOptions.clear();
    delete repository.status;
    this.t4cRepoService
      .stopRepository(repository.instance_id, repository.id)
      .pipe(
        tap(() => (repository.status = 'OFFLINE')),
        switchMap(() =>
          this.t4cRepoService.getT4CRepositories(this.instance!.id)
        )
      )
      .subscribe((repositories) => {
        this.t4cRepoService._repositories.next(repositories);
      });
  }

  recreateRepository(repository: T4CServerRepository): void {
    this.repositoryList.selectedOptions.clear();
    delete repository.status;
    this.t4cRepoService
      .recreateRepository(repository.instance_id, repository.id)
      .pipe(
        tap(() => (repository.status = 'ONLINE')),
        switchMap(() =>
          this.t4cRepoService.getT4CRepositories(this.instance!.id)
        )
      )
      .subscribe((repositories) => {
        this.t4cRepoService._repositories.next(repositories);
      });
  }

  get selectedRepository(): T4CRepository & T4CServerRepository {
    return this.repositoryList.selectedOptions.selected[0].value;
  }

  ngOnDestroy(): void {
    this.t4cRepoService._repositories.next([]);
  }
}
