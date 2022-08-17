/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpErrorResponse } from '@angular/common/http';
import { Component, Input, OnInit } from '@angular/core';
import {
  GitModel,
  GitModelService,
} from 'src/app/services/modelsources/git-model/git-model.service';
import {
  JenkinsPipeline,
  JenkinsService,
} from 'src/app/services/backups/jenkins/jenkins.service';

@Component({
  selector: 'app-jenkins-backup-settings',
  templateUrl: './jenkins-backup-settings.component.html',
  styleUrls: ['./jenkins-backup-settings.component.css'],
})
export class JenkinsBackupSettingsComponent implements OnInit {
  constructor(
    private jenkinsService: JenkinsService,
    private gitModelService: GitModelService
  ) {}

  ngOnInit(): void {}

  /* TODO: Needs rework

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

  refreshPipeline() {
    this.loading = true;
    if (this.repository) {
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
  } */
}
