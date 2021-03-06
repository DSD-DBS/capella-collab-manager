// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class JenkinsService {
  constructor(private http: HttpClient) {}

  getJenkinsPipelineForModel(
    repository: string,
    model_id: number
  ): Observable<JenkinsPipeline> {
    return this.http.get<JenkinsPipeline>(
      `${environment.backend_url}/projects/${repository}/extensions/backups/jenkins`
    );
  }

  createJenkinsPipelineForModel(
    repository: string,
    model_id: number
  ): Observable<JenkinsPipeline> {
    return this.http.post<JenkinsPipeline>(
      `${environment.backend_url}/projects/${repository}/extensions/backups/jenkins`,
      null
    );
  }

  createJenkinsJobForModel(
    repository: string,
    model_id: number,
    pipeline_name: string
  ): Observable<void> {
    return this.http.post<void>(
      `${environment.backend_url}/projects/${repository}/extensions/backups/jenkins/${pipeline_name}/jobs`,
      null
    );
  }

  removeJenkinsPipeline(
    repository: string,
    model_id: number,
    pipeline_name: string
  ): Observable<void> {
    return this.http.delete<void>(
      `${environment.backend_url}/projects/${repository}/extensions/backups/jenkins/${pipeline_name}`
    );
  }
}

export interface JenkinsPipeline {
  id: number;
  name: string;
  latest_run: JenkinsPipelineRun;
}
export interface JenkinsPipelineRun {
  id: number;
  result: string;
  start_time: string;
  logs_url: string;
}
