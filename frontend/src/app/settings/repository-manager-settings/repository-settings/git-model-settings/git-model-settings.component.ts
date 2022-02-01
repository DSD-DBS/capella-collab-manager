import { Component, Input, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import {
  GitModel,
  GitModelService,
} from 'src/app/services/git-model/git-model.service';
import { JenkinsService } from 'src/app/services/jenkins/jenkins.service';
import { RepositoryProject } from 'src/app/services/repository-project/repository-project.service';
import { GitModelDeletionDialogComponent } from './git-model-deletion-dialog/git-model-deletion-dialog.component';

@Component({
  selector: 'app-git-model-settings',
  templateUrl: './git-model-settings.component.html',
  styleUrls: ['./git-model-settings.component.css'],
})
export class GitModelSettingsComponent implements OnInit {
  createGitModel = new FormGroup({
    name: new FormControl('', Validators.required),
    project_id: new FormControl('', Validators.required),
    model: new FormGroup({
      path: new FormControl('', [Validators.required, this.gitURLValidator()]),
      entrypoint: new FormControl('', [
        Validators.required,
        this.airdFileValidator(),
      ]),
      revision: new FormControl('', Validators.required),
    }),
    create_backup_job: new FormControl(false),
  });

  _projects: Array<RepositoryProject> = [];
  @Input()
  set projects(value: Array<RepositoryProject>) {
    this._projects = value;
    this.refreshGitModels();
  }

  get projects() {
    return this._projects;
  }

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

  gitModels: Array<GitModel> = [];

  constructor(
    private gitModelService: GitModelService,
    private jenkinsService: JenkinsService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.refreshGitModels();
  }

  refreshGitModels() {
    this.gitModelService
      .getGitRepositoriesForRepository(this.repository)
      .subscribe((res) => {
        this.gitModels = res;
      });
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

  assignGitModel() {
    if (this.createGitModel.valid) {
      this.gitModelService
        .assignGitRepositoryToRepository(
          this.repository,
          this.createGitModel.value
        )
        .subscribe((res) => {
          if (this.createGitModel.value.create_backup_job) {
            this.jenkinsService
              .createJenkinsPipelineForModel(this.repository, res.id)
              .subscribe(() => {
                this.refreshGitModels();
              });
          } else {
            this.refreshGitModels();
          }
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
