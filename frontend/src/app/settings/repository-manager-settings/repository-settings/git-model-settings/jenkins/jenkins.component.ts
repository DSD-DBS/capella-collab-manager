import { HttpErrorResponse } from '@angular/common/http';
import { Component, Input, OnInit } from '@angular/core';
import { GitModel } from 'src/app/services/git-model/git-model.service';
import {
  JenkinsPipeline,
  JenkinsService,
} from 'src/app/services/jenkins/jenkins.service';

@Component({
  selector: 'app-jenkins',
  templateUrl: './jenkins.component.html',
  styleUrls: ['./jenkins.component.css'],
})
export class JenkinsComponent implements OnInit {
  _model: GitModel | undefined = undefined;

  @Input()
  set model(value: GitModel | undefined) {
    this._model = value;
    this.refreshPipeline();
  }

  get model() {
    return this._model;
  }

  loading = true;
  pipeline: JenkinsPipeline | undefined = undefined;

  _repository = '';

  @Input()
  set repository(value: string) {
    this._repository = value;
    this.refreshPipeline();
  }

  get repository() {
    return this._repository;
  }

  constructor(private jenkinsService: JenkinsService) {}

  ngOnInit(): void {}

  refreshPipeline() {
    this.loading = true;
    if (this.model && this.repository) {
      this.jenkinsService
        .getJenkinsPipelineForModel(this.repository, this.model.id)
        .subscribe(
          (res) => {
            this.pipeline = res;
            this.loading = false;
          },
          (err: HttpErrorResponse) => {
            this.loading = false;
            if (err.status === 404) {
              this.pipeline = undefined;
            }
          }
        );
    }
  }

  createPipeline() {
    if (this.model && this.repository) {
      this.loading = true;
      this.jenkinsService
        .createJenkinsPipelineForModel(this.repository, this.model.id)
        .subscribe(
          () => {
            this.refreshPipeline();
            this.loading = false;
          },
          () => {
            this.loading = false;
          }
        );
    }
  }

  runJenkinsJob() {
    if (this.model && this.pipeline && this.repository) {
      this.loading = true;
      this.jenkinsService
        .createJenkinsJobForModel(
          this.repository,
          this.model.id,
          this.pipeline.name
        )
        .subscribe(
          () => {
            this.refreshPipeline();
            this.loading = false;
          },
          () => {
            this.loading = false;
          }
        );
    }
  }

  removeJenkinsPipeline() {
    if (this.model && this.pipeline && this.repository) {
      this.loading = true;
      this.jenkinsService
        .removeJenkinsPipeline(
          this.repository,
          this.model.id,
          this.pipeline.name
        )
        .subscribe(
          () => {
            this.refreshPipeline();
            this.loading = false;
          },
          () => {
            this.loading = false;
          }
        );
    }
  }
}
