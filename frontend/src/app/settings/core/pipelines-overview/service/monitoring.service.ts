/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { PipelineRunStatus } from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class MonitoringService {
  constructor(private httpClient: HttpClient) {}
  fetchGeneralHealth(): Observable<GeneralHealth> {
    return this.httpClient.get<GeneralHealth>(
      `${environment.backend_url}/health/general`
    );
  }

  fetchModelHealth(): Observable<ToolmodelStatus[]> {
    return this.httpClient.get<ToolmodelStatus[]>(
      `${environment.backend_url}/health/models`
    );
  }

  fetchProjectHealth(): Observable<ProjectStatus[]> {
    return this.httpClient.get<ProjectStatus[]>(
      `${environment.backend_url}/health/projects`
    );
  }
}

export type GeneralHealth = {
  guacamole: boolean;
  database: boolean;
  operator: boolean;
};

export type ToolmodelStatus = {
  project_slug: string;
  model_slug: string;

  warnings: string[];
  primary_git_repository_status: GitModelStatus;
  pipeline_status: PipelineRunStatus;
  model_badge_status: ModelModifierStatus;
  diagram_cache_status: ModelModifierStatus;
};

export type ProjectStatus = {
  project_slug: string;

  warnings: string[];
};

export type ModelModifierStatus =
  | 'success'
  | 'failure'
  | 'unconfigured'
  | 'unsupported';

export type GitModelStatus = 'accessible' | 'inaccessible' | 'unset';
