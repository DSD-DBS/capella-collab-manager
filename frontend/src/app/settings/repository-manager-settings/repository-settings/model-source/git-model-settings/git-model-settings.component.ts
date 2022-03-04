import { Component, Input, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  FormGroupDirective,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import {
  GitModel,
  GitModelService,
} from 'src/app/services/modelsources/git-model/git-model.service';
import { T4CRepoService } from 'src/app/services/modelsources/t4c-repos/t4c-repo.service';
import { GitModelDeletionDialogComponent } from './git-model-deletion-dialog/git-model-deletion-dialog.component';

@Component({
  selector: 'app-git-model-settings',
  templateUrl: './git-model-settings.component.html',
  styleUrls: ['./git-model-settings.component.css'],
})
export class GitModelSettingsComponent implements OnInit {
  createGitModel = new FormGroup({
    name: new FormControl('', Validators.required),
    model: new FormGroup({
      path: new FormControl('', [Validators.required, this.gitURLValidator()]),
      entrypoint: new FormControl('', [
        Validators.required,
        this.airdFileValidator(),
      ]),
      revision: new FormControl('', Validators.required),
    }),
    credentials: new FormGroup({
      username: new FormControl(''),
      password: new FormControl(''),
    }),
  });

  get model(): FormGroup {
    return this.createGitModel.get('model') as FormGroup;
  }

  get gitPath(): FormControl {
    return this.model.get('path') as FormControl;
  }

  get entrypoint(): FormControl {
    return this.model.get('entrypoint') as FormControl;
  }

  @Input()
  repository = '';

  constructor(
    public gitModelService: GitModelService,
    private dialog: MatDialog,
    public t4cService: T4CRepoService
  ) {}

  ngOnInit(): void {
    this.refreshGitModels();
  }

  refreshGitModels() {
    this.gitModelService
      .getGitRepositoriesForRepository(this.repository)
      .subscribe();
  }

  gitURLValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const regex = /^https:\/\/\S*\.git$/;
      if (regex.test(control.value) || !control.value) {
        return null;
      }
      return { gitURLError: true };
    };
  }

  airdFileValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const regex = /\.aird$/;
      if (regex.test(control.value) || !control.value) {
        return null;
      }
      return { airdFileIncorrect: true };
    };
  }

  assignGitModel(formDirective: FormGroupDirective) {
    if (this.createGitModel.valid) {
      this.gitModelService
        .assignGitRepositoryToRepository(
          this.repository,
          this.createGitModel.value
        )
        .subscribe(() => {
          formDirective.resetForm();
          this.createGitModel.reset();
          this.refreshGitModels();
        });
    }
  }

  unassignGitModel(model: GitModel) {
    const dialogRef = this.dialog.open(GitModelDeletionDialogComponent, {
      data: { model: model, repository: this.repository },
    });

    dialogRef.afterClosed().subscribe((val) => {
      if (val) {
        this.refreshGitModels();
      }
    });
  }

  makeItPrimary(id: number) {
    this.gitModelService
      .makeGitRepositoryPrimary(this.repository, id)
      .subscribe(() => {
        this.refreshGitModels();
      });
  }
}
