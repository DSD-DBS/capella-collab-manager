/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
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
import { RouterModule } from '@angular/router';
import { CreateT4CRepository, T4CInstance } from 'src/app/openapi';
import {
  ExtendedT4CRepository,
  ExtendedT4CRepositoryStatus,
  T4CRepositoryWrapperService,
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
    MatIconButton,
    MatTooltip,
    ReactiveFormsModule,
    MatError,
    AsyncPipe,
    RouterModule,
  ],
})
export class T4CInstanceSettingsComponent implements OnChanges, OnDestroy {
  @Input() instance?: T4CInstance;

  search = '';

  repositoryCreationInProgress = false;

  constructor(
    public t4cRepoService: T4CRepositoryWrapperService,
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
    repositories: ExtendedT4CRepository[] | undefined | null,
  ): ExtendedT4CRepository[] | undefined {
    if (repositories === undefined || repositories === null) {
      return undefined;
    }

    return repositories.filter((repository) =>
      repository.name.toLowerCase().includes(this.search.toLowerCase()),
    );
  }

  createRepository(): void {
    this.repositoryCreationInProgress = true;
    if (this.form.valid) {
      this.t4cRepoService
        .createRepository(
          this.instance!.id,
          this.form.value as CreateT4CRepository,
        )
        .subscribe({
          next: () => {
            this.form.reset();
            this.repositoryCreationInProgress = false;
          },
          error: () => (this.repositoryCreationInProgress = false),
        });
    }
  }

  deleteRepository(repository: ExtendedT4CRepository): void {
    this.dialog.open(T4CRepoDeletionDialogComponent, {
      data: repository,
    });
  }

  startRepository(repository: ExtendedT4CRepository): void {
    this.t4cRepoService
      .startRepository(repository.instance.id, repository.id)
      .subscribe();
  }

  stopRepository(repository: ExtendedT4CRepository): void {
    this.t4cRepoService
      .stopRepository(repository.instance.id, repository.id)
      .subscribe();
  }

  recreateRepository(repository: ExtendedT4CRepository): void {
    this.t4cRepoService
      .recreateRepository(repository.instance.id, repository.id)
      .subscribe();
  }

  mapStatusToText(status: ExtendedT4CRepositoryStatus | null): StatusMapping {
    switch (status) {
      case 'LOADING':
        return {
          icon: 'sync',
          text: 'Hang tight while we refresh the list.',
        };
      case 'INITIAL':
        return { icon: 'cloud_upload', text: 'Repository is started.' };
      case 'INSTANCE_UNREACHABLE':
        return { icon: 'sync_problem', text: 'The instance is unreachable.' };
      case 'NOT_FOUND':
        return {
          icon: 'block',
          text: 'Repository not found on the TeamForCapella server.',
        };
      case 'OFFLINE':
        return { icon: 'cloud_off', text: 'Repository is offline.' };
      case 'ONLINE':
        return { icon: 'cloud_queue', text: 'Repository is up & running' };
      case null:
        return { icon: 'error', text: 'Unknown status' };
    }
  }
}

interface StatusMapping {
  icon: string;
  text: string;
}
