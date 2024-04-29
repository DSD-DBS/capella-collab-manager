/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgFor, NgIf, AsyncPipe } from '@angular/common';
import {
  Component,
  OnDestroy,
  ViewChild,
  Input,
  OnChanges,
  SimpleChanges,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import {
  MatFormField,
  MatLabel,
  MatSuffix,
  MatError,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatSelectionList } from '@angular/material/list';
import { MatTooltip } from '@angular/material/tooltip';
import { T4CInstance } from 'src/app/services/settings/t4c-instance.service';
import {
  CreateT4CRepository,
  T4CRepoService,
  T4CRepository,
  T4CServerRepository,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { T4CRepoDeletionDialogComponent } from './t4c-repo-deletion-dialog/t4c-repo-deletion-dialog.component';

@Component({
  selector: 'app-t4c-instance-settings',
  templateUrl: './t4c-instance-settings.component.html',
  styleUrls: ['./t4c-instance-settings.component.css'],
  standalone: true,
  imports: [
    MatButton,
    MatIcon,
    MatFormField,
    MatLabel,
    MatInput,
    FormsModule,
    MatSuffix,
    NgFor,
    NgIf,
    MatIconButton,
    MatTooltip,
    ReactiveFormsModule,
    MatError,
    AsyncPipe,
  ],
})
export class T4CInstanceSettingsComponent implements OnChanges, OnDestroy {
  @Input() instance?: T4CInstance;

  search = '';

  constructor(
    public t4cRepoService: T4CRepoService,
    private dialog: MatDialog,
  ) {}

  ngOnChanges(_changes: SimpleChanges): void {
    if (this.instance) {
      this.t4cRepoService.loadRepositories(this.instance.id);
    }
  }

  ngOnDestroy(): void {
    this.t4cRepoService.reset();
  }

  @ViewChild('repositoryList') repositoryList!: MatSelectionList;

  form = new FormGroup({
    name: new FormControl('', {
      validators: [Validators.required, Validators.pattern(/^[-a-zA-Z0-9_]+$/)],
      asyncValidators: this.t4cRepoService.asyncNameValidator(),
    }),
  });

  getFilteredRepositories(
    repositories: T4CServerRepository[] | undefined | null,
  ): T4CServerRepository[] | undefined {
    if (repositories === undefined || repositories === null) {
      return undefined;
    }

    return repositories.filter((repository) =>
      repository.name.toLowerCase().includes(this.search.toLowerCase()),
    );
  }

  createRepository(): void {
    if (this.form.valid) {
      this.t4cRepoService
        .createRepository(
          this.instance!.id,
          this.form.value as CreateT4CRepository,
        )
        .subscribe(() => this.form.reset());
    }
  }

  deleteRepository(repository: T4CRepository): void {
    this.dialog.open(T4CRepoDeletionDialogComponent, {
      data: repository,
    });
  }

  startRepository(repository: T4CServerRepository): void {
    this.t4cRepoService
      .startRepository(repository.instance.id, repository.id)
      .subscribe();
  }

  stopRepository(repository: T4CServerRepository): void {
    this.t4cRepoService
      .stopRepository(repository.instance.id, repository.id)
      .subscribe();
  }

  recreateRepository(repository: T4CServerRepository): void {
    this.t4cRepoService
      .recreateRepository(repository.instance.id, repository.id)
      .subscribe();
  }
}
